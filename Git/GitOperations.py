import git
import re
import os
from datetime import datetime
from urllib.request import Request, urlopen
import sys
import subprocess
from Git import credentials

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
def getCommitsDatesForThisReq(localRepo, reqName):
  return getGitLogInfo(localRepo, reqName, _getCommitsDatesForThisReq)

'''
A public function exposed to other scripts
Compare two dates in the format of '%Y-%m-%dT%H:%M:%S'
'''
def compareGitDates(date1, date2):
  return datetime.strptime(date1,
                           '%Y-%m-%dT%H:%M:%S') >= datetime.strptime(date2,
                                                                     '%Y-%m-%dT%H:%M:%S')
'''
Git API Request with PAT
'''
def requestByGitAPiWithAuth(url):
  request = Request(url)
  request.add_header("Authorization", "token %s" % credentials.personal_access_tokens)
  response = urlopen(request)
  return response.read()

'''
Execute git command by using Tika's local repo.
'''
def executeGitShellCommand(localRepo, commandList):
  pr = subprocess.Popen(commandList,
                        cwd=localRepo,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
  out, err = pr.communicate()
  decodedErr = err.decode("utf-8")
  if (len(re.findall('(no such commit)', decodedErr)) > 0):
    # It's true, if no branches contains a commit.
    return ""
  elif (len(re.findall('(HEAD is now at )([a-zA-Z0-9]+)', decodedErr)) > 0):
    return decodedErr
  elif (decodedErr != ""):
    print("Error from _executeGitShellCommand")
    sys.exit(decodedErr)
  return out.decode("ISO-8859-1")

'''
It clones a local branch on localRepo/gitProjectName by using gitCloneURL
'''
def cloneAndPull(localRepo, gitProjectName, gitCloneURL):
  repoDir = localRepo + gitProjectName
  if not os.path.isdir(repoDir) and not os.path.exists(repoDir):
    git.Git().clone(gitCloneURL.format(gitProjectName), repoDir)
  git.cmd.Git(repoDir).pull()

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
