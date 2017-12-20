from Git import GitOperations
import re
from Utility import Utility


class GitApache:
    gitCloneURL = None
    localRepo = None
    allUnmergedAndClosedPullRequests = []
    gitProjectName = None
    _Git_API_URL = "https://api.github.com/repos/apache/{}/pulls?state={}&per_page=100&page="
    PULL_REQUESTS_BY_PAGE = None
    CLOSED_PULL_REQUEST_BY_PAGE = None

    '''
    gitCloneURL - an url for http calls
    localRepos - a local copy of a project
    gitProjectName - for formatting a url of git api.
    '''

    def __init__(self, gitCloneURL, localRepo, gitProjectName):
        print("initializing gitProjectName = ", gitProjectName)
        print("initializing gitCloneURL = ", gitCloneURL)
        print("initializing localRepo = ", localRepo)
        GitOperations.cloneAndPull(
            localRepo, Utility.getGoodWindowFileName(gitProjectName), gitCloneURL)
        self.gitCloneURL = gitCloneURL
        self.localRepo = localRepo
        self.gitProjectName = gitProjectName
        self.PULL_REQUESTS_BY_PAGE = self._Git_API_URL.format(
            gitProjectName, "all")
        self.CLOSED_PULL_REQUEST_BY_PAGE = self._Git_API_URL.format(
            gitProjectName, "closed")

    '''
    PERILS-27
    '''

    def getPortionOfCommitsThroughMasterBranch(self):
        totalNumCommitOnMaster = int(GitOperations.executeGitShellCommand(
            self.localRepo, ["git rev-list --count master"]))
        allShaOnMaster = GitOperations.executeGitShellCommand(
            self.localRepo, ["git log --pretty=format:'%H'"]).split("\n")
        totalNumCommitThroughMaster = 0
        for sha in allShaOnMaster:
            print ("sha = ", sha)
            if self.__isCommittedThroughMaster(sha):
                totalNumCommitThroughMaster += 1
            else:
                print("not committed through master = ", sha)
        if self.__checkIfTheLatestCommitCommittedThroughMaster():
            totalNumCommitOnMaster += 1
        print("totalNumCommitOnMaster = ", totalNumCommitOnMaster)
        print("totalNumCommitThroughMaster = ", totalNumCommitThroughMaster)
        return (totalNumCommitOnMaster, totalNumCommitThroughMaster)

    '''
    Multiple commits might be made by the same developer.
        This function is to not print the same name multiple times.
    '''

    def getUniqueDevelopers(self, reqName):
        developers = GitOperations.getGitLogInfo(self.localRepo,
                                                 reqName,
                                                 self.__getGitDeveloperForThisReq)
        developerSet = set()
        print("developers = ", developers)
        for dev in developers["formattedDevelopers"]:
            developerSet.add(dev)
        return developerSet

    '''
    Get the percentage of pull requests merged by Heuristic 1
    H1 - At least one of the commits in the pull request appears in the target project’s master branch.
    Idea:
        1. Get all the commits of a pull request
        2. Check if any one of the commits appears in the master
    '''

    def getPercentageByH1(self):
        h1Merged = []
        for pr in self.__getAllUnmergedAndClosedPullRequests():
            hasAddedThisPr = False
            commitDict = Utility.convertDictStringToDict(
                GitOperations.requestByGitAPIWithAuth(pr["commits_url"]))
            for commit in commitDict:
                if self.__isInMasterBranch(commit["sha"]) and not hasAddedThisPr:
                    h1Merged.append(pr)
                    hasAddedThisPr = True
        return len(h1Merged) / len(self.allUnmergedAndClosedPullRequests)

    '''
    Get the percentage of pull requests merged by Heuristic 2
    H2 - A commit closes the pull request using its log and that commit appears in the master branch.
        This means that the pull request commits were squashed onto one commit and this commit was merged.
    '''

    def getPercentageByH2(self):
        h2Merged = []
        for pr in self.__getAllUnmergedAndClosedPullRequests():
            hasAddedThisPr = False
            commitDict = Utility.convertDictStringToDict(
                GitOperations.requestByGitAPIWithAuth(pr["commits_url"]))
            for commit in commitDict:
                if self.__isInMasterBranch(commit["sha"]) and \
                        self.__hasClosingKeyword(commit["sha"]) and \
                        not hasAddedThisPr:
                    h2Merged.append(pr)
                    hasAddedThisPr = True
        return len(h2Merged) / len(self.allUnmergedAndClosedPullRequests)

    '''
    Get the percentage of pull requests merged by Heuristic 3
    H3 - One of the last three discussion comments contain a commit unique identifier.
        This commit appears in the project's master branch, 
        and the corresponding comment can be matched by the following regular expression.
    '''

    def getPercentageByH3(self):
        commitCount = 0
        h3Merged = []
        for pr in self.__getAllUnmergedAndClosedPullRequests():
            hasAddedThisPr = False
            commitDict = Utility.convertDictStringToDict(
                GitOperations.requestByGitAPIWithAuth(pr["commits_url"]))
            for commit in commitDict:
                if (self.__isInMasterBranch(commit["sha"]) and
                    self.__hasMergedKeyword(commit["sha"]) and
                        not hasAddedThisPr):
                    h3Merged.append(pr)
                    hasAddedThisPr = False
                if commitCount == 2:
                    break
        return len(h3Merged) / len(self.allUnmergedAndClosedPullRequests)

    '''
    Get the percentage of pull requests merged by Heuristic 4
    H4 - The latest comment (on the master) prior to closing the pull request matches the regular expression.
    '''

    def getPercentageByH4(self):
        mergedByH4 = []
        for pr in self.__getAllUnmergedAndClosedPullRequests():
            out = GitOperations.executeGitShellCommand(self.localRepo,
                                                       ["git rev-list -1 --before=" + pr["closed_at"] + " master"])
            if self.__hasMasterBranch() != 0 and self.__hasMergedKeyword(out):
                mergedByH4.append(pr)
        return len(mergedByH4) / len(self.allUnmergedAndClosedPullRequests)

    '''
    Get the percentage of pull requests closed through GitHub
    '''

    def getPortionOfUnmergedPullRequestOnGitHub(self):
        return len(self.__getAllUnmergedAndClosedPullRequests()) / len(self.__getAllPullRequestsByPaging())

    '''
    For PERIL-27, repos that don't have master branches
    '''

    def getNumberBranches(self):
        numBranch = None
        if self.__hasMasterBranch() == 0:
            return 0
        else:
            numBranch = GitOperations.executeGitShellCommand(self.localRepo,
                                                             ["git branch -a | grep \'remote\' | wc -l"])
            return int(re.sub(r'\s+', '', numBranch))

    '''
    Check if a repo has a master. If it doesn't return 0.
    '''

    def __hasMasterBranch(self):
        numBranch = GitOperations.executeGitShellCommand(self.localRepo,
                                                         ["git branch -a | grep \'master\' | wc -l"])
        return int(re.sub(r'\s+', '', numBranch))

    '''
    Get unmerged and closed pull requests
    '''

    def __getAllUnmergedAndClosedPullRequests(self):
        if len(self.allUnmergedAndClosedPullRequests) == 0:
            nonMergedPullRequest = []
            for pullRequest in self.__getAllClosedPullRequestByPaging():
                if pullRequest["merged_at"] == None:
                    nonMergedPullRequest.append(pullRequest)
            self.allUnmergedAndClosedPullRequests = nonMergedPullRequest
        return self.allUnmergedAndClosedPullRequests

    '''
    Get developers for this requirement.
    '''

    def __getGitDeveloperForThisReq(self, logInfo):
        developers = re.findall('(?<=Author: )([a-zA-Z ]+)', logInfo)
        formattedDevelopers = []
        for dev in developers:  # delete the last white space character detected by the regex
            formattedDevelopers.append(dev[:-1])

        return {"formattedDevelopers": formattedDevelopers}

    '''
    Get all pull requests by paging
    '''

    def __getAllPullRequestsByPaging(self):
        page = 0
        allPullRequestDict = []
        while True:
            pullRequestsOnePageDict = Utility.convertDictStringToDict(
                GitOperations.requestByGitAPIWithAuth(self.PULL_REQUESTS_BY_PAGE + str(page)))
            if len(pullRequestsOnePageDict) == 0:
                break
            else:
                allPullRequestDict += pullRequestsOnePageDict
            page += 1

        return allPullRequestDict

    '''
    Get all the closed pull requests by paging
    '''

    def __getAllClosedPullRequestByPaging(self):
        page = 0
        allPullRequestDict = []
        while True:
            pullRequestsOnePageDict = Utility.convertDictStringToDict(
                GitOperations.requestByGitAPIWithAuth(self.CLOSED_PULL_REQUEST_BY_PAGE + str(page)))
            if len(pullRequestsOnePageDict) == 0:
                break
            else:
                allPullRequestDict += pullRequestsOnePageDict
            page += 1

        return allPullRequestDict

    '''
    Check if a commit is in the master branch

    @return a boolean that indicates if a commit is on the master branch of the project
    '''

    def __isInMasterBranch(self, commitSha):
        out = GitOperations.executeGitShellCommand(
            self.localRepo, ["git branch --all --contains", commitSha])
        return len(re.findall('(master)', out)) > 0

    '''
    A parent function for _hasClosingKeyword and _hasMergedKeyword
    '''

    def __hasKeywordInGitLogByRegex(self, commitSha, regex):
        consoleOut = GitOperations.executeGitShellCommand(self.localRepo,
                                                          ["git show", commitSha])
        pattern = re.compile(regex)
        return pattern.match(consoleOut) != None

    '''
    Check if the comment of a commit has one of the closing keywords
    '''

    def __hasClosingKeyword(self, commitSha):
        return self.__hasKeywordInGitLogByRegex(commitSha,
                                                '(?:close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)')

    '''
    Check if the comment of a commit has one of the merging keywords.
    '''

    def __hasMergedKeyword(self, commitSha):
        return self.__hasKeywordInGitLogByRegex(commitSha, "(?:Note: checking out ')([A-Za-z0-9]+)(')")

    '''
    This function is to handle the fact that git-when-merged can't detect the last commit on a branch.
    Logic of this algorithm:
        The last commit the master branch must be a normal commit if it's a merge commit.
    '''

    def __checkIfTheLatestCommitCommittedThroughMaster(self):
        oneLineCommit = GitOperations.executeGitShellCommand(
            self.localRepo, ["git log --oneline -n 1"])
        output = re.search("(Merge) (branch|pull)", oneLineCommit)
        return output == None

    '''
    Check if the passed sha is committed directly from master
    '''

    def __isCommittedThroughMaster(self, sha):
        consoleOutput = GitOperations.executeGitShellCommand(
            self.localRepo, ["git when-merged -l {}".format(sha)])
        isDirectCommit = 0
        isMergedMaster = 0
        if consoleOutput != None:
            isDirectCommit = len(re.findall(
                "(master                      Commit is directly on this branch.)",
                consoleOutput)) > 0
            isMergedMaster = len(re.findall(
                "(Merge branch 'master')", consoleOutput)) > 0
            print("isDirectCommit = ", isDirectCommit)
            print("isMergedMaster = ", isMergedMaster)
        return isDirectCommit or isMergedMaster
