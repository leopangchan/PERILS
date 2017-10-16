# PERILS

### Abstract
Github and JIRA have become the most important sources for software engineering researches. However, there are potential perils of mining data from them. We defined a set of perils in order to help people measure the validity of the data.

### Get Started
The project requires two local storages. One for a local branch for each Apache project's Git repo. One for a local folder that output the csv file. Please configure these two urls in config.py before run the project.


### Technologies Used
1. GitPython API - https://github.com/gitpython-developers/GitPython
It uses local repositories. Cloning is done automatically through cloneAndPull in GitOperations.py. 
Please make sure local branches exist in case of errors.
2. Github API - https://developer.github.com/v3/
It uses HTTP calls with authorization header in requestByGitAPIWithAuth in GitOperations.py.
3. JIRA API - https://developer.atlassian.com/jiradev/jira-apis/jira-rest-apis
The scripts executes JQL. All the JQLs are in JiraQuery.py.

