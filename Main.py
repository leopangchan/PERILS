import json
from Git import GitOperations
import re
from Utility import Utility
import config
from ProjectApache import ProjectApache

_APACHE_GITHUB = "https://github.com/apache/{}"

# def __validGitRepo(repoURL):
#   gitUrlByRegex = re.findall("(?:.*)(https?.*)", eachRepo)
#   if len(re.findall("(git:)(:?.*)", eachRepo)) > 0:  # Valid git clone url.
#     return
#     urlInfo["repository"].append(gitUrlByRegex[0])
#     localRepos.append(config.LOCAL_REPO.format(projectName))
#   elif len(gitUrlByRegex) > 0:  # git clone ulr with https
#     urlInfo["repository"].append(gitUrlByRegex[0])
#     localRepos.append(config.LOCAL_REPO.format(projectName))
#   elif eachRepo.find("svn") > 0:  # might have svn mirror
#     svnName = re.findall(".*/asf/(.*)(?:/)", eachRepo)[0]
#     if GitOperations.isValidGitCloneURL(_APACHE_GITHUB.format(svnName)):
#       urlInfo["repository"].append(_APACHE_GITHUB.format(svnName))
#       localRepos.append(config.LOCAL_REPO.format(projectName))
#   else:
#     print("No git repo or svn mirror found for ", projectName)
'''
It loops all the projects in apache-project.json.
'''
def main():
  with open("./Dataset/apache-projects.json", encoding="utf8") as dataFile:
    projectData = json.load(dataFile)
    # loop through all the projects in apache-projects.json
    for projectName, info in projectData.items():
      urlInfo = {"repository":[], "jira":""}
      bugDatabase = info["bug-database"] if "bug-database" in info else "" # get information about the bug database
      urlInfo["jira"] = bugDatabase if bugDatabase.find("jira") >= 0 else None
      repos = info["repository"] if "repository" in info else [] # get information about the repositories
      localRepos = []
      for eachRepo in repos:
        gitUrlByRegex = re.findall("(?:.*)(https?.*)", eachRepo)
        if len(re.findall("(git:)(:?.*)", eachRepo)) > 0: # Valid git clone url.
          urlInfo["repository"].append(gitUrlByRegex[0])
          localRepos.append(config.LOCAL_REPO.format(projectName))
        elif len(gitUrlByRegex) > 0: # git clone ulr with https
          urlInfo["repository"].append(gitUrlByRegex[0])
          localRepos.append(config.LOCAL_REPO.format(projectName))
        elif eachRepo.find("svn") > 0: # might have svn mirror
          svnName = re.findall(".*/asf/(.*)(?:/)", eachRepo)[0]
          #TODO Handle "http://svn.apache.org/repos/asf/httpcomponents/httpclient/trunk" in a regex
          if GitOperations.isValidGitCloneURL(_APACHE_GITHUB.format(svnName)):
            urlInfo["repository"].append(_APACHE_GITHUB.format(svnName))
            localRepos.append(config.LOCAL_REPO.format(projectName))
        else:
          print ("No git repo or svn mirror found for ", projectName)

      # either of jira or git repo is not available.
      if (urlInfo["jira"] == None or len(urlInfo["repository"]) == 0):
        continue

      proj = ProjectApache(urlInfo["jira"],
                           urlInfo["repository"],
                           config.CSV_URL,
                           localRepos)
      Utility.prettyPrintJSON(Utility.getCurrentRateLimit())
      proj.toCSVFile()
    dataFile.close()

if __name__ == "__main__":
  main()
