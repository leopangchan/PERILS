from Git.GitApache import GitApache
from Jira.JiraApache import JiraApache
from CSV import CSV
import re
import Utility
import sys

class ProjectApache:
  localRepos = None
  jiraApache = None
  gitsApache = []
  csv = None
  columns = None

  def __init__(self, jiraURL, gitURLs, csvURL, localRepos):
    self.localRepos = localRepos
    self.columns = self.__initCSVHeaders()
    self.jiraApache = JiraApache(re.findall(".*\/(.*)", jiraURL)[0])
    if (len(localRepos) != len(gitURLs)):
      sys.exit("the number of local repos doesn't match with the number of git urls.")
    for index, gitUrl in enumerate(gitURLs):
      print (gitUrl)
      self.gitsApache.append(GitApache(gitUrl, localRepos[index],
                                       re.findall(".*\/(.*).git", gitUrl)[0]))
    self.csv = CSV(csvURL, self.__initCSVHeaders(), self.__initCSVRows())

  # it initializes a list of strings of the headers
  def __initCSVHeaders(self):
    columnsNames = [
      'numOpenRequirements',
      'numInProgressRequirements',
      'ticket',
      # PERILS-6
      'numDevelopers',
      # PERILS-12
      'numDevelopedRequirementsBeforeThisInProgress',
      # PERILS-11
      'numDescOpen',
      'numDescInProgress',
      'numDescResolved',
      'numDescReopened',
      'numDescClosed',
      # PERILS-3
      "numCommitsOpen",
      "numCommitsInProgress",
      "numCommitsResolved",
      "numCommitsReopened",
      "numCommitsClosed",
      # PERILS-16
      "numOpenWhileThisOpen",
      "numInProgressWhileThisOpen",
      "numResolvedWhileThisOpen",
      "numReopenedWhileThisOpen",
      "numClosedWhileThisOpen",
      # PERILS-7
      "numOpenWhenInProgress",
      "numInProgressWhenInProgress",
      "numReopenedWhenInProgress",
      "numResolvedWhenInProgress",
      "numClosedWhenInProgress"]
    columnsNames += Utility.getAllPossibleTransitions()
    return columnsNames

  '''
    for each issue in issues of jiraApache
      row = columnsName
      perilsResults = issue.getJIRAItemsHistory()
      align all the columns in row in perilsResults
      row[numOpenRequirements] = jiraApache.getNumOpenFeatures
      row[numInProgressRequirements] = jiraApache.getNumInProgressFeatures
      row[numDevelopers] = self.gitsApache.getNumUniqueDevelopers(issue.reqNAme)
    return the row dict to al CSV project
  '''
  def __initCSVRows(self):
    for issue in self.jiraApache.getAllIssuesApache():
      row = {key : None for key in self.__initCSVHeaders()}
      perilsRestuls = issue.getPerilsResults(self.localRepos)
      row["numOpenRequirements"] = self.jiraApache.getNumOpenFeatures()
      row["numInProgressRequirements"] = self.jiraApache.getNumInProgressFeatures()
      totalNumDevelopersInAllRepos = 0
      for gitApache in self.gitsApache:
        totalNumDevelopersInAllRepos += gitApache.getNumUniqueDevelopers(issue.reqName)
      row["numDevelopers"] = totalNumDevelopersInAllRepos
      row["numDevelopedRequirementsBeforeThisInProgress"] = perilsRestuls["numDevelopedRequirementsBeforeThisInProgress"]
      row["numOpenWhileThisOpen"] = perilsRestuls['numOpenWhileThisOpen']
      row["numInProgressWhileThisOpen"] = perilsRestuls['numInProgressWhileThisOpen']
      row["numResolvedWhileThisOpen"] = perilsRestuls['numResolvedWhileThisOpen']
      row["numReopenedWhileThisOpen"] = perilsRestuls['numReopenedWhileThisOpen']
      row["numClosedWhileThisOpen"] = perilsRestuls['numClosedWhileThisOpen']
      row["numOpenWhenInProgress"] = perilsRestuls['numOpenWhenInProgress']
      row["numInProgressWhenInProgress"] = perilsRestuls["numInProgressWhenInProgress"]
      row["numReopenedWhenInProgress"] = perilsRestuls["numReopenedWhenInProgress"]
      row["numResolvedWhenInProgress"] = perilsRestuls["numResolvedWhenInProgress"]
      row["numClosedWhenInProgress"] = perilsRestuls["numClosedWhenInProgress"]
      for key in perilsRestuls["numDescChangedCounters"]:
        row["numDesc{}".format(key.replace(" ", ""))] = perilsRestuls["numDescChangedCounters"][key]
      for key in perilsRestuls["transitionCounters"]:
        row[key] = perilsRestuls["transitionCounters"][key]
      for key in perilsRestuls["numCommitsEachStatus"]:
        row["numCommits{}".format(key.replace(" ", ""))] = perilsRestuls["numCommitsEachStatus"][key]

      return row
  '''
  It output all metrics to a csv file.
  '''
  def toCSVFile(self):
    # fd = open('document.csv', 'a')
    # fd.write(myCsvrow)
    # fd.close()
    return self.csv.outputCSVFile()
