from bdb import set_trace
from inspect import trace
from pprint import pprint
import gitlab
from atlassian import Bitbucket
from dotenv import load_dotenv
import os


load_dotenv()

bitbucket = Bitbucket(
    url=os.getenv("BITBUCKET_URL"),
    username=os.getenv("BITBUCKET_USERNAME"),
    password=os.getenv("BITBUCKET_PASSWORD")
)

gl = gitlab.Gitlab(os.getenv("GITLAB_URL"), os.getenv("GITLAB_TOKEN"))  #Added
gl.auth()

bb_json = []

bb_projects = bitbucket.project_list()

bb_repo_branch = {}
gl_repo_branch = {}

for bb_project in bb_projects:
    repositories = bitbucket.repo_list(bb_project["key"])
    for repo in repositories:
        gl_project = [project for project in gl.projects.list(search=repo["slug"]) if project.attributes["name"] == repo["slug"]][0]
        # print(gl_project)
        bb_branches = bitbucket.get_branches(bb_project["key"], repo["slug"])
        for bb_branch in bb_branches:
            bb_repo_branch[repo["slug"]] = bb_repo_branch.get(repo["slug"],[])
            bb_repo_branch[repo["slug"]].append(bb_branch['displayId'])

projects = gl.projects.list()
for project in projects:
    branches = project.branches.list()
    for branch in branches:
        gl_repo_branch[project.name] = gl_repo_branch.get(project.name, [])
        gl_repo_branch[project.name].append(branch.name)
        gl_repo_branch[project.name] = sorted(gl_repo_branch[project.name])
print(gl_repo_branch)

# print(bb_repo_branch)


# projects = gl.projects.list(search='repo_v1')
# print(projects)