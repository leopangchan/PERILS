from Git import GitOperations
import re
from Jira import JiraQuery
import collections
import Utility

class IssueApache:
    END_TIME_STR = "endTime"
    START_TIME_STR = "startTime"
    TRANSITIONS = None  # a <transition>|<transition2> of dictionary

    ### Global variables for storing data while loop history of a requirenment ###
    histories = None
    currentStatus = None
    descriptionChangedCounters = 0
    startProgressTime = None # PERILS-7 && PERILS-12 && PERILS-16
    openEndingTime = None # PERILS-16
    transitionCounters = None # PERILS-2
    openTimeTracking = None # PERILS-3
    statusTracking = None # PERILS-3
    isJustOpen = False # PERILS-3
    dateRangeEachState = None # PERILS-3

    reqName = None
    jiraAPI = None
    jiraProjectName = None

    def __init__(self, reqName, jiraAPI, projectName):
        self.reqName = reqName
        self.jiraAPI = jiraAPI
        self.jiraProjectName = projectName
        self.TRANSITIONS = Utility.getAllPossibleTransitions()

    def getStatusOfOtherReqBeforeThisInProgress(self):
        self.__getHistoryItems(self.__initStartInProgressTime)
        result = {}
        if self.startProgressTime != None:
            allIssueBeforeThis = JiraQuery.getAllFinishedIssueBeforeThisInProgress(self.jiraAPI,
                                                                                   self.jiraProjectName,
                                                                                   self.startProgressTime)
            numIssueBeforeThis = len(allIssueBeforeThis)
            result["numDevelopedRequirementsBeforeThisInProgress"] = numIssueBeforeThis
        else:  # this issue has no "In Progress" phase.
            result["numDevelopedRequirementsBeforeThisInProgress"] = "NA"
        return result

    '''
    Goal: To init data for PERILS-7 - Statuses of other existing requirements
    A public wrapper for _getStatuesOfOtherReqWhenThisInProgress()
    '''
    def getStatuesOfOtherReqWhenThisInProgress(self):
        self.__getHistoryItems(self.__initStartInProgressTime)
        result = {}
        if self.startProgressTime != None:
            timeClause = " ON " + re.findall('(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', START_PROGRESS_TIME)[0]
            result["numOpenWhenInProgress"] = JiraQuery.getNumIssueWhileOpenByClause(self.jiraAPI, timeClause)
            result["numInProgressWhenInProgress"] = JiraQuery.getNumIssueWhenInProgressByClause(self.jiraAPI, timeClause)
            result["numReopenedWhenInProgress"] = JiraQuery.getNumIssueWhileReopenedByClause(self.jiraAPI, timeClause)
            result["numResolvedWhenInProgress"] = JiraQuery.getNumIssueWhileResolvedByClause(self.jiraAPI, timeClause)
            result["numClosedWhenInProgress"] = (self.jiraAPI, timeClause)
        else: # The issue hasn't started being developed.
            result["numOpenWhenInProgress"] = result["numInProgressWhenInProgress"] = result[
                "numReopenedWhenInProgress"] = "NA"
            result["numResolvedWhenInProgress"] = result["numClosedWhenInProgress"] = "NA"
        return result

    '''
    Goal: To resolve PERILS-2: transitions
    '''
    def getNumEachTransition(self):
        self.__getHistoryItems(self.__initNumEachTransition)
        return self.transitionCounters

    '''
    Goal: To resolve PERILS-16 - Statuses of other requirements when open
    '''
    def getOtherReqStatusesWhileThisOpen(self, jira, reqName):
        self.__getHistoryItems(self._initFinishedOpenStatusTime)
        result = {}
        timeClause = ""
        if self.openEndingTime != None:  # the issue is in open status without activities
            timeClause = " BEFORE " + re.findall('(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', self.openEndingTime)[0]
        result["numOpenWhileThisOpen"] = JiraQuery.getNumIssueWhileOpenByClause(self.jiraAPI, timeClause)
        result["numInProgressWhileThisOpen"] = JiraQuery.getNumIssueWhenInProgressByClause(self.jiraAPI, timeClause)
        result["numReopenedWhileThisOpen"] = JiraQuery.getNumIssueWhileReopenedByClause(self.jiraAPI, timeClause)
        result["numResolvedWhileThisOpen"] = JiraQuery.getNumIssueWhileResolvedByClause(self.jiraAPI, timeClause)
        result["numClosedWhileThisOpen"] = JiraQuery.getNumIssueWhileClosedByClause(self.jiraAPI, timeClause)
        return result

    '''
    Goal: To resolve PERILS-3 - Workflow compliance
      How many times a commit related to the requirement happened while the requirement was: 
        open, in progress, closed, resolved, reopened.
    '''
    def getNumCommitDuringEachStatus(self):
        self.__getHistoryItems(self.__initDateRangeEachStatus)
        return self.__getNumCommitEachStatusByDateRange(GitOperations.getCommitsDatesForThisReq(self.reqName))

    '''
    Goal: To resolve PERILS-11 - Changed.
    A public wrapper for _initNumDescriptionChangedCounter()
    '''
    def getNumDescriptionChanged(self, reqName):
        currentStatus = Utility.OPEN_STR
        for history in self.histories:
            for indx, item in enumerate(history.items):
                if (item.field == "description"):
                    self.descriptionChangedCounters[currentStatus] += 1
                if (item.field == Utility.STATE_STR):
                    currentStatus = item.toString
        return self.descriptionChangedCounters

    '''
    Goal: To resolve PERILS-12
    '''
    def __initStartInProgressTime(self, item, createdTime):
        global START_PROGRESS_TIME
        if item.field == Utility.STATE_STR:
            if (item.toString == Utility.IN_PROGRESS_STR):
                START_PROGRESS_TIME = createdTime

    '''
    Goal: To resolved PERILS-2
    '''
    def __initNumEachTransition(self, item, _):
        global TRANSITION_COUNTERS
        key = self.currentStatus + "|" + item.toString
        TRANSITION_COUNTERS[key] += 1

    def __getHistoryItems(self, callback):
        self._initHistories()
        self._initCounters()
        result = {}
        self.currentStatus = Utility.OPEN_STR
        for history in self.histories:
            createdTime = re.findall('(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', history.created)[0]
            for indx, item in enumerate(history.items):
                if (item.field == Utility.STATE_STR and self.currentStatus != item.toString):
                    result = callback(item, createdTime)
                if (item.field == Utility.STATE_STR):
                    self.currentStatus = item.toString
        return result

    '''
    Goal: To resolve PERILS-16 - Statuses of other requirements when open
    '''
    def _initFinishedOpenStatusTime(self, item, createdTime):
        if self.currentStatus == Utility.OPEN_STR and item.toString != Utility.OPEN_STR:  # Resolved #6
            self.openEndingTime = createdTime

    '''
    Goal: To resolvde PERILS-3 - Work compliance
    Logic:
      1. Get the time ranges of each status
      2. Find all the commits
      3. Align commits with the time ranges
    '''
    def __initDateRangeEachStatus(self, item, createdTime):
      # fromString means one status starts, and toString means one status ends.
      if self.statusTracking == item.fromString: # End one status
        self.dateRangeEachState[item.fromString].append({self.END_TIME_STR: createdTime})
      elif item.fromString == Utility.OPEN_STR and self.isJustOpen == False:# A newly open ticket has no transition so I have to record the endTime of "Open" in a edge case.
        self.dateRangeEachState[item.fromString] = [{self.END_TIME_STR: createdTime}]
        self.isJustOpen = True
      if item.toString not in self.dateRangeEachState:
        self.dateRangeEachState[item.toString] = [{self.START_TIME_STR: createdTime}] # start one new status
        self.statusTracking = item.toString
      else:
        self.dateRangeEachState[item.toString].append({self.START_TIME_STR: createdTime})
        self.statusTracking = item.toString

    '''
    Goal: To get all commits within the time ranges of a status
    Restraints: Two statuses might share the same date, so one commit could count twice.
    '''

    def __getNumCommitEachStatusByDateRange(self, commitDates):
        numCommitEachStatus = {}
        hasRecordedDateDict = {}

        for key in Utility.STATUSES:  # init the counter for each status
            numCommitEachStatus[key] = 0

        if "numCommits" in commitDates and commitDates['numCommits'] == 0:
            return numCommitEachStatus

        for commitNdx, commitDate in enumerate(commitDates):
            for key, timeList in self.dateRangeEachState.items():
                for oneDateRange in self.__formatTimeList(timeList):
                    if commitNdx not in hasRecordedDateDict:
                        if self.END_TIME_STR not in oneDateRange and \
                                GitOperations.compareGitDates(commitDate, oneDateRange[self.END_TIME_STR]):  # Example: a resolved issue that still have commits
                            numCommitEachStatus[key] += 1
                            hasRecordedDateDict[commitNdx] = True
                        elif self.END_TIME_STR in oneDateRange and \
                                GitOperations.compareGitDates(oneDateRange[self.END_TIME_STR], commitDate):
                            numCommitEachStatus[key] += 1
                            hasRecordedDateDict[commitNdx] = True
                        elif self.END_TIME_STR not in oneDateRange and \
                                GitOperations.compareGitDates(oneDateRange[self.END_TIME_STR], commitDate):
                            numCommitEachStatus[key] += 1
                            hasRecordedDateDict[commitNdx] = True

        return numCommitEachStatus

    '''
    Goal: A helper for getNumCommittEachStatusByDateRange()
    '''

    def __formatTimeList(self, timeList):
        dateRanges = []
        oneDateRange = {}

        for ndx, val in enumerate(timeList):  # formate a pair of startTime and endTime into one dict
            if self.START_TIME_STR not in oneDateRange and self.START_TIME_STR not in val:
                oneDateRange[self.END_TIME_STR] = val[self.END_TIME_STR]
            elif self.START_TIME_STR not in oneDateRange and self.START_TIME_STR in val:
                oneDateRange[self.START_TIME_STR] = val[self.START_TIME_STR]
            elif self.END_TIME_STR not in oneDateRange and self.END_TIME_STR in val:
                oneDateRange[self.END_TIME_STR] = val[self.END_TIME_STR]

            if (ndx + 1) % 2 == 0:
                dateRanges.append(oneDateRange)
                oneDateRange = {}
            elif ndx == (len(timeList) - 1):
                dateRanges.append(oneDateRange)
                oneDateRange = {}

        return dateRanges

    '''
    Goal: A call to JIRA API to get the changelog
    '''
    def _initHistories(self):
        issue = self.jiraAPI.issue(self.reqName, expand='changelog')
        self.histories = issue.changelog.histories

    '''
    Goal: init all counter for each requirenment. 
    '''
    def _initCounters(self):
        self.descriptionChangedCounters = {}
        self.transitionCounters = {}
        self.startProgressTime = None
        self.openEndingTime = None  # PERILS-16
        self.openTimeTracking = self.statusTracking = None  # PERILS-3
        self.isJustOpen = False  # PERILS-3
        self.dateRangeEachState = collections.OrderedDict()  # PERILS-3
        self.dateRangeEachState.clear()

        for key in Utility.STATUSES:
            self.descriptionChangedCounters[key] = 0
        # initialize transitionCounters
        for key in self.TRANSITIONS:
            TRANSITION_COUNTERS[key] = 0
