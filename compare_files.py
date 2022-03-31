from importlib.metadata import requires
from optparse import Values
from pprint import pprint
import requests
from requests.auth import HTTPBasicAuth
import gitlab
from atlassian import Bitbucket
from dotenv import load_dotenv
import os
import pandas as pd
from pprint import pprint
load_dotenv()

bitbucket = Bitbucket(
    url=os.getenv("BITBUCKET_URL"),
    username=os.getenv("BITBUCKET_USERNAME"),
    password=os.getenv("BITBUCKET_PASSWORD")
)

bb_files = {}
bb_projects = bitbucket.project_list()

for project in bb_projects:
    proj_key = project["key"]
    repos = bitbucket.repo_list(proj_key)
    for repo in repos:
        repo_name=repo['name']
        bb_files[repo_name] = {}
        branches = bitbucket.get_branches(proj_key, repo.get("name"), details=False)
        for branch in branches:
            branch_name=branch['displayId']
            url="http://localhost:7990/rest/api/1.0/projects/{}/repos/{}/files?at={}".format(proj_key,repo_name,branch_name)
            request = requests.get(url,auth=HTTPBasicAuth(os.getenv("BITBUCKET_USERNAME"), os.getenv("BITBUCKET_PASSWORD")))
            data = request.json()
            bb_files[repo_name][branch['displayId']] = data['values']
print(bb_files)

# print("bitbucket",bb_files)
bb_fi=[]

gl = gitlab.Gitlab(os.getenv("GITLAB_URL"), os.getenv("GITLAB_TOKEN"))

gl.auth()
projects = gl.projects.list()

git_files = {}

for project in projects:
    branches = project.branches.list()
    files_list = {}
    git_files[project.attributes['name']]={}
    for branch in branches:
        git_files[project.attributes['name']][branch.name]=[]
        items = project.repository_tree(path="", recursive=True, all=True, ref=branch.name)
        for item in items:
            if item["type"] != "tree":
                if branch.name not in files_list:
                    files_list[branch.name] = []
                files_list[branch.name].append(item["path"])
                files_list[branch.name] = sorted(files_list[branch.name])
        git_files[project.attributes['name']][branch.name]=files_list[branch.name]

report={"branch":[], "files":[], "difference_location":[]}
for key,value in bb_files.items():
    gitlab_files_list=git_files.get(key,value)
    bb_files_list=bb_files.get(key,value)
    
    for branch in bb_files_list:
        if branch in gitlab_files_list:
            if gitlab_files_list[branch] != bb_files_list[branch]:        
                report["branch"].append(branch)
                report["files"].append(bb_files_list[branch])
                report["difference_location"].append("Gitlab")

        else:
            report["branch"].append(branch)
            report["files"].append(bb_files_list[branch])
            report["difference_location"].append("Gitlab")
report=pd.DataFrame(report)

if len(report):  
    print(report)
else:
    print("NO DIFFERENCES FOUND")