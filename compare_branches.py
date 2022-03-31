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

projects = bitbucket.project_list()

bb_repo_branch = {}
gl_repo_branch = {}

for project in projects:
    # print(project)
    repositories = bitbucket.repo_list(project["key"])
    for repo in repositories:
        branches = bitbucket.get_branches(project["key"], repo["slug"])
        branches = sorted([branch["displayId"] for branch in branches])
        
        bb_repo_branch[repo["slug"]] = branches


projects = gl.projects.list()
for project in projects:
    branches = project.branches.list()
    for branch in branches:
        gl_repo_branch[project.name] = gl_repo_branch.get(project.name, [])
        gl_repo_branch[project.name].append(branch.name)
        gl_repo_branch[project.name] = sorted(gl_repo_branch[project.name])


# print(bb_repo_branch)
# print(gl_repo_branch)




for repo, branches in bb_repo_branch.items():
    if repo not in gl_repo_branch:
        # print("Repository '{}' is not present on gitlab".format(bb_repo_branch))
        continue
    
    extra_branch = set(branches) - set(gl_repo_branch[repo])
    if extra_branch:
        print("Branches {} are not available on repo '{}' on gitlab".format(", ".join(extra_branch), repo))
from pdb import Pdb