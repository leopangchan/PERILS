import git
import re
from datetime import datetime

'''
The parent of getting git's logInfo.
      It gets logs of all commits that contain the string of the requirement.
'''
def getGitLogInfo(localRepo, reqName, callback):
  repo = git.Repo(localRepo)
  logInfo = repo.git.log("--all", "-i", "--grep=" + reqName)
  if(len(logInfo) == 0):
    return {"formattedDevelopers": [], "datesForAllCommits": [], "numCommits": 0}
  else:
    return callback(logInfo)

'''
A public function exposed to other scripts
'''
def getCommitsDatesForThisReq(reqName):
  return getGitLogInfo(reqName, _getCommitsDatesForThisReq)
'''
Get all the commits' dates of this requirement.
'''
def _getCommitsDatesForThisReq(logInfo):
  dates = re.findall('(?<=Date:   )([A-Za-z0-9: ]+)', logInfo)
  datesForAllCommits = []
  for date in dates:
    datesForAllCommits.append(datetime.strptime(date[:-1],
                                                "%a %b %d %H:%M:%S %Y").strftime('%Y-%m-%dT%H:%M:%S'))

  return datesForAllCommits

'''
A public function exposed to other scripts
Compare two dates in the format of '%Y-%m-%dT%H:%M:%S'
'''
def compareGitDates(date1, date2):
  return datetime.strptime(date1,
                           '%Y-%m-%dT%H:%M:%S') >= datetime.strptime(date2,
                                                                     '%Y-%m-%dT%H:%M:%S')
