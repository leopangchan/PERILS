from Git.GitApache import GitApache
from Jira.JiraApache import JiraApache
from CSV import CSV
import Utility

class ProjectApache:
  localRepo = None
  jiraApache = None
  gitApache = None
  csv = None
  columns = None

  def __init__(self, jiraURL, gitURL, csvURL, localRepo):
    self.localRepo = localRepo
    self.columns = self.__initCSVHeaders()
    self.jiraApache = JiraApache(jiraURL)
    self.gitApache = GitApache(gitURL)
    self.csv = CSV(csvURL, self.__initCSVHeaders(), self. __initCSVRows())

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

  # It initializes a dictionary that have data for each column defined in __initCSVHeaders.
  def __initCSVRows(self):
    return self.jiraApache.toCSVDict()

  '''
  It output all metrics to a csv file.
  for each issue in issues of jiraApache
    row = columnsName
    perilsResults = issue.getJIRAItemsHistory()
    align all the columns in row in perilsResults
    row[numOpenRequirements] = jiraApache.getNumOpenFeatures
    row[numInProgressRequirements] = jiraApache.getNumInProgressFeatures
    row[numDevelopers] = self.gitApache.getNumUniqueDevelopers(issue.reqNAme)
    pass the row dict to al CSV project
    call outputCSVFile()
    
    
  '''
  def toCSVFile(self):
    # fd = open('document.csv', 'a')
    # fd.write(myCsvRow)
    # fd.close()
    return self.csv.outputCSVFile()
