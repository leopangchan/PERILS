import json
from Git import GitOperations
import re
import sys
import config
from ProjectApache import ProjectApache

_APACHE_GITHUB = "https://github.com/apache/{}"

'''
It loops all the projects in apache-project.json.
'''
def main():
  with open("apache-projects.json", encoding="utf8") as dataFile:
    projectData = json.load(dataFile)
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
          svnName = re.findall(".*\/asf\/(.*)?\/?", eachRepo)[0]
          svnName = svnName.replace("/", "")
          if GitOperations.isValidURL(_APACHE_GITHUB.format(svnName)):
            urlInfo["repository"].append(_APACHE_GITHUB.format(svnName))
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
