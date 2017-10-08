import re

JIRA_REQ_WHERE_CLAUSE = "project={} AND issueType=\'New Feature\'"
JIRA_REQ_CONT_WHERE_CLAUSE = JIRA_REQ_WHERE_CLAUSE + " AND "
MAX_RESULTS = 1000

###################### PUBLIC APIs ######################
def getAllIssues(jira):
  return jira.search_issues(JIRA_REQ_WHERE_CLAUSE)

def getNumIssueWhileOpenByClause(jira, projectName, clause=""):
  return len(jira.search_issues(JIRA_REQ_CONT_WHERE_CLAUSE.format(projectName) + "status WAS \'Open\'" + clause,
                                maxResults=MAX_RESULTS))

def getNumIssueWhenInProgressByClause(jira, projectName, clause=""):
  return len(jira.search_issues(JIRA_REQ_CONT_WHERE_CLAUSE.format(projectName) + "status WAS \'In Progress\'" + clause,
                                maxResults=MAX_RESULTS))

def getNumIssueWhileReopenedByClause(jira, projectName, clause=""):
  return len(jira.search_issues(JIRA_REQ_CONT_WHERE_CLAUSE.format(projectName) + "status WAS \'Reopened\'" + clause,
                                maxResults=MAX_RESULTS))

def getNumIssueWhileResolvedByClause(jira, projectName, clause=""):
  return len(jira.search_issues(JIRA_REQ_CONT_WHERE_CLAUSE.format(projectName) + "status WAS \'Resolved\'" + clause,
                                maxResults=MAX_RESULTS))

def getNumIssueWhileClosedByClause(jira, projectName, clause=""):
  return len(jira.search_issues(JIRA_REQ_CONT_WHERE_CLAUSE.format(projectName) + "status WAS \'Closed\'" + clause,
                                maxResults=MAX_RESULTS))


def getAllFinishedIssueBeforeThisInProgress(jira, projectName, startProgressTime):
  return jira.search_issues(JIRA_REQ_CONT_WHERE_CLAUSE.format(projectName) +
                                                    "status WAS IN (\'Resolved\', \'Closed\') BEFORE " +
                                                    re.findall('(\d{4}-\d{2}-\d{2})', startProgressTime)[0],
                                                    maxResults=MAX_RESULTS)