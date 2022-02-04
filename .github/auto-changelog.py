import os
import requests
import json
import subprocess

#Reading env variables from GitHub Workflow step
GITHUB_URL = os.environ['GITHUB_URL']
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
GIT_BRANCH = os.environ['GITHUB_BRANCH']
GITHUB_REPO_PATH = os.environ['GITHUB_REPO_PATH']
PRERELEASE_VERSION = os.environ['PRERELEASE_VERSION']
RELEASE_DATE = os.environ['RELEASE_DATE']

GITHUB_AUTH = 'Bearer ' + GITHUB_TOKEN
GITHUB_GET_HEADER = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": GITHUB_AUTH,
}
GITHUB_PAYLOAD_HEADER = {
    **GITHUB_GET_HEADER,
    "Content-Type": "application/json",
}

configFile = open('.github/changelog_config.json')
configJSON = json.load(configFile)
configFile.close()
featBranches = configJSON["branch_prefixes"]["features"]
fixBranches = configJSON["branch_prefixes"]["fixes"]
notes_content = []
fileVars = []
source_branches = []
source_branches_type = []

print("Finding Github Latest Release Tag....")
get_latest_release_url = GITHUB_URL + "/repos/" + GITHUB_REPO_PATH + "/releases/latest"
get_latest_release_resp = requests.request(
    "GET", get_latest_release_url, headers=GITHUB_GET_HEADER
)
print("Get Latest Release Status Code: " + str(get_latest_release_resp.status_code))
latest_release_tag = get_latest_release_resp.json().get("tag_name")
print("GitHub Latest Release Tag: " + str(latest_release_tag))
print("---------------------------------------------------------")

commitsMsgs = subprocess.getoutput("git log '" + latest_release_tag + "'...'" + PRERELEASE_VERSION + "' --pretty=oneline --format='* %C(auto) %h %s by (%an)'")
commitsLines = commitsMsgs.splitlines()
commitsLines[-1] = commitsLines[-1] + "\n"
print("Git Log Diff between " + latest_release_tag + " and " + PRERELEASE_VERSION + "...\n" + commitsMsgs)

for commit in commitsLines:
    commit_sha = commit.split(" ")[2]
    commit_branches = subprocess.getoutput(
        "git branch -a --contains " + commit_sha + " --sort=-committerdate --format='%(refname:lstrip=-2)'"
    )
    commit_first_branch = commit_branches.splitlines()[0]
    source_branches.append(commit_first_branch)
    print("Commit " + commit_sha + "comes from branch: " + commit_first_branch)

for branch in source_branches:
    branch_type = branch.split("/")[0].lower()
    if branch_type in featBranches:
        branch_type = "features"
    elif branch_type in fixBranches:
        branch_type = "fixes"
    else:
        branch_type = "misc"
    source_branches_type.append(branch_type)
    print("Git Branch " + branch + " -> type: " + branch_type)

print("Creating release notes content...")
notes_content.append(configJSON["file_title"] + "\n")
for section in configJSON["sections"]:
    notes_content.append(section["header"] + "\n")
    if section["type"] in source_branches_type:
        for i, commit_branch_type in enumerate(source_branches_type):
            if section["type"] == commit_branch_type:
                notes_content.append(commitsLines[i])
    else:
        notes_content.append(section["default"] + "\n")

for footer in configJSON["footer_rows"]:
    notes_content.append(footer + "\n")
notes_content = [row + "\n" for row in notes_content]
releaseNotes = ''.join(notes_content)

print("Identifying release notes variables...")
for arg in configJSON["env_variables"]:
    if arg == "{RELEASE_DATE}":
        fileVars.append(RELEASE_DATE)
    elif arg == "{GIT_REPO}":
        fileVars.append(GITHUB_REPO_PATH)
    elif arg == "{RELEASE_TAG}":
        fileVars.append(PRERELEASE_VERSION)

for i, each in enumerate(configJSON["env_variables"]):
    releaseNotes = releaseNotes.replace(each, fileVars[i])

print("---------------------------------------------------------")
print("Release Notes Content")
print("---------------------------------------------------------")
print(releaseNotes)
print("---------------------------------------------------------")

print("Finding Github Release with generated Tag....")
getReleaseURL = GITHUB_URL + "/repos/" + GITHUB_REPO_PATH + "/releases/tags/" + PRERELEASE_VERSION
getReleaseResp = requests.request("GET", getReleaseURL, headers=GITHUB_GET_HEADER)
print("Get Release Status Code: " + str(getReleaseResp.status_code))
releaseId = getReleaseResp.json().get("id")
print("GitHub Release ID: " + str(releaseId))
print("---------------------------------------------------------")

print("Patching GitHub Release with Release Notes content")
patchReleaseURL = GITHUB_URL + "/repos/" + GITHUB_REPO_PATH + "/releases/" + str(releaseId)
patchReleasePayload = json.dumps({
  "tag_name": PRERELEASE_VERSION,
  "body": releaseNotes
})

pathReleaseResp = requests.request("PATCH", patchReleaseURL, headers=GITHUB_PAYLOAD_HEADER, data=patchReleasePayload)
print("Patch Request Status Code: " + str(pathReleaseResp.status_code))
if (pathReleaseResp.status_code == 200):
    print("GitHub Release Notes updated!!!")
else:
    print("Patch Release Notes failed!!!... manually open the release and edit its contents:\n")

print("Release URL: https://github.com/" + GITHUB_REPO_PATH + "/releases/tag/" + PRERELEASE_VERSION)