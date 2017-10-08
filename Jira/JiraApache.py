from jira import JIRA
from Jira.IssueApache import IssueApache
from Jira import JiraQuery


class JiraApache:
  jiraAPI = None
  jiraURL = None
  jiraProjectName = None
  issuesApache = []

  def __init__(self, jiraURL, jiraProjectName):
    self.jiraURL = jiraURL
    self.jiraAPI = JIRA({
      'server': self.jiraURL
    })
    self.jiraProjectName = jiraProjectName
    self.__setAllIssuesApache(self.jiraAPI)

  '''
  Goal: To resolve this question (No related ticket in JIRA):
    The number of requirenments that are in progress.
  '''
  def getNumInProgressFeatures(self):
    return JiraQuery.getNumIssueWhenInProgressByClause(self.jiraAPI, self.jiraProjectName)

  '''		
  Goal: To resolve this question (No related ticket in JIRA):
    how many requirements are already defined in Jira but their implementation has not started yet.		
  '''
  def getNumOpenFeatures(self):
    return JiraQuery.getNumIssueWhileOpenByClause(self.jiraAPI, self.jiraProjectName)

  '''
  Return all issues of in this jira
  '''
  def getAllIssuesApache(self):
    return self.issuesApache

  def __setAllIssuesApache(self, jiraAPI):
    for req in JiraQuery.getAllIssues(self.jiraAPI):
      self.issuesApache.append(IssueApache(req.key, jiraAPI))
