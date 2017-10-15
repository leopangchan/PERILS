import json
from Git import GitOperations
import re
import sys
import config
from ProjectApache import ProjectApache

'''
It loops all the projects in apache-project.json.
'''
def main():
  with open("tika-projects.json", encoding="utf8") as dataFile:
    projectData = json.load(dataFile)
    # Utility.prettyPrintJSON(projectData)
    # loop through all the projects in apache-projects.json
    for projectName, info in projectData.items():
      urlInfo = {"repository":[], "jira":""}
      bugDatabase = info["bug-database"] if "bug-database" in info else "" # get information about the bug database
      urlInfo["jira"] = bugDatabase if bugDatabase.find("jira") >= 0 else None
      repos = info["repository"] if "repository" in info else [] # get information about the repositories

      localRepos = []
      for eachRepo in repos:
        if len(re.findall(".*\/(.*).git", eachRepo)) > 0:
          urlInfo["repository"].append(eachRepo)
          localRepos.append(config.LOCAL_REPO.format(projectName))
        elif eachRepo.find("svn") > 0:
          # extract the svn's name.
          # uses the svn's name as a key in attempt to access a mirrored git repo.
          # append git://git.apache.org/<svn's name>.git
          svnName = re.findall(".*\/asf\/(.*)?\/?", eachRepo)[0]
          svnName = svnName.replace("/", "")
          if GitOperations.isValidURL("https://git.apache.org/repos/asf/{}.git".format(svnName.replace("/", ""))):
            urlInfo["repository"].append("https://git.apache.org/repos/asf/{}.git".format(svnName.replace("/", "")))
            localRepos.append(config.LOCAL_REPO.format(projectName))

      # either of jira or git repo is not available.
      if (urlInfo["jira"] == None or len(urlInfo["repository"]) == 0):
        continue

      proj = ProjectApache(urlInfo["jira"],
                           urlInfo["repository"],
                           config.CSV_URL,
                           localRepos)
      proj.toCSVFile()
    dataFile.close()

if __name__ == "__main__":
  main()