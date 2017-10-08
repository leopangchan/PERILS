import json
import config
from ProjectApache import ProjectApache

# TODO handle either of jira or repo is not available.

def main():
  with open("apache-projects.json", encoding="utf8") as dataFile:

    projectData = json.load(dataFile)
    # loop through all the projects in apache-projects.json
    for projectName, info in projectData.items():
      urlInfo = {"repository":[], "jira":""}
      bugDatabase = info["bug-database"] if "bug-database" in info else ""
      repos = info["repository"] if "repository" in info else []
      urlInfo["jira"] = bugDatabase if bugDatabase.find("jira") >= 0 else None

      for eachRepo in repos:
        if eachRepo.find("git") >= 0:
          urlInfo["repository"].append(eachRepo)
        elif eachRepo.find("svn") >= 0:
          # TODO handle mirrored repos
          urlInfo["repository"].append("")
      localRepo = config.LOCAL_REPO.format(projectName)
      proj = ProjectApache(urlInfo["jira"], urlInfo["repository"], "", localRepo)
      proj.toCSVFile()
    dataFile.close()

if __name__ == "__main__":
  main()