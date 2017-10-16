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
    for index, gitUrl in enumerate(gitURLs):
      self.gitsApache.append(GitApache(gitUrl, localRepos[index],
                                       re.findall(".*\/(.*).git", gitUrl)[0]))
    self.rowsDict = self.__initCSVRows()
    self.csv = CSV(csvURL, self.__initCSVHeaders(), self.rowsDict)

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
    allRows = []
    count = 0
    for issue in self.jiraApache.getAllIssuesApache():
      if count == 2:
         break
      row = {key : None for key in self.__initCSVHeaders()}
      perilsResults = issue.getPerilsResults(self.localRepos)
      row["ticket"] = issue.reqName
      row["numOpenRequirements"] = self.jiraApache.getNumOpenFeatures()
      row["numInProgressRequirements"] = self.jiraApache.getNumInProgressFeatures()
      totalNumDevelopersInAllRepos = 0
      for gitApache in self.gitsApache:
        totalNumDevelopersInAllRepos += gitApache.getNumUniqueDevelopers(issue.reqName)
      row["numDevelopers"] = totalNumDevelopersInAllRepos
      row["numDevelopedRequirementsBeforeThisInProgress"] = perilsResults["numDevelopedRequirementsBeforeThisInProgress"]
      row["numOpenWhileThisOpen"] = perilsResults['numOpenWhileThisOpen']
      row["numInProgressWhileThisOpen"] = perilsResults['numInProgressWhileThisOpen']
      row["numResolvedWhileThisOpen"] = perilsResults['numResolvedWhileThisOpen']
      row["numReopenedWhileThisOpen"] = perilsResults['numReopenedWhileThisOpen']
      row["numClosedWhileThisOpen"] = perilsResults['numClosedWhileThisOpen']
      row["numOpenWhenInProgress"] = perilsResults['numOpenWhenInProgress']
      row["numInProgressWhenInProgress"] = perilsResults["numInProgressWhenInProgress"]
      row["numReopenedWhenInProgress"] = perilsResults["numReopenedWhenInProgress"]
      row["numResolvedWhenInProgress"] = perilsResults["numResolvedWhenInProgress"]
      row["numClosedWhenInProgress"] = perilsResults["numClosedWhenInProgress"]
      for key in perilsResults["numDescChangedCounters"]:
        row["numDesc{}".format(key.replace(" ", ""))] = perilsResults["numDescChangedCounters"][key]
      for key in perilsResults["transitionCounters"]:
        row[key] = perilsResults["transitionCounters"][key]
      for key in perilsResults["numCommitsEachStatus"]:
        row["numCommits{}".format(key.replace(" ", ""))] = perilsResults["numCommitsEachStatus"][key]
      allRows.append(row)
      count += 1
      # TODO: uses allRows to get each ratio of column for each PERIL
    return allRows


  '''
  It calculates the sum of all values in a column for colName.
  @param colName - the name of a column for which the sum is calculated
  '''
  def getColumnSum(colName):
    r = [item[colName] for item in self.rowsDict]
    print ("list of columnSum = ", r)
    return sum(r)

  '''
  It loops a list of colName to the sum of values of columns for a peril. 
  @param colNames - a list of colNames for a peril
  '''
  def getPERILSum(colNames):
    allColumnsSum = 0
    for colName in colNames:
      allColumnsSum += getColumnSum(colName)
    return allColumnsSum

  '''
  Calculate the ratio of colName's sum / allColumnsSum
  @param colName - the column for which a ratio is calculated
  @param colNames - the columns of a peril that colName belongs to
  '''
  def getRatioForOneColumnOfPERIL(colName, colNames):
    return getColumnSum(colName) / getPERILSum(colNames)

  '''
  It output all metrics to a csv file.
  '''
  def toCSVFile(self):
    # fd = open('document.csv', 'a')
    # fd.write(myCsvrow)
    # fd.close()
    return self.csv.outputCSVFile()
