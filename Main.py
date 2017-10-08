import json
import re
import config
from ProjectApache import ProjectApache


def main():
  with open("apache-projects.json", encoding="utf8") as dataFile:

    projectData = json.load(dataFile)
    # loop through all the projects in apache-projects.json
    for projectName, info in projectData.items():
      urlInfo = {"repository":[], "jira":""}
      # get information about the bug database
      bugDatabase = info["bug-database"] if "bug-database" in info else ""
      urlInfo["jira"] = bugDatabase if bugDatabase.find("jira") >= 0 else None
      # get information about the repositories
      repos = info["repository"] if "repository" in info else []
      localRepos = []
      for eachRepo in repos:
        if len(re.findall(".*\/(.*).git", eachRepo)) > 0:
          urlInfo["repository"].append(eachRepo)
          localRepos.append(config.LOCAL_REPO.format(projectName))
        elif eachRepo.find("svn") > 0:
          # TODO handle mirrored repos
          urlInfo["repository"].append("")

      # either of jira or git repo is not available.
      if (urlInfo["jira"] == None or len( urlInfo["repository"]) == 0):
        continue

      proj = ProjectApache(urlInfo["jira"],
                           urlInfo["repository"],
                           config.CSV_URL,
                           localRepos)
      proj.toCSVFile()
    dataFile.close()

if __name__ == "__main__":
  main()