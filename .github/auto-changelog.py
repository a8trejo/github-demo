import os
import requests
import json
import subprocess

GITHUB_URL = os.environ['GITHUB_URL']
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
GIT_BRANCH = os.environ['GITHUB_BRANCH']
GITHUB_REPO_PATH = os.environ['GITHUB_REPO_PATH']
PRERELEASE_VERSION = os.environ['PRERELEASE_VERSION']
RELEASE_DATE = os.environ['RELEASE_DATE']
GITHUB_AUTH = 'Bearer ' + GITHUB_TOKEN

configFile = open('.github/changelog_config.json')
configJSON = json.load(configFile)
configFile.close()
branchType = GIT_BRANCH.split("/")[0].lower()
featBranches = configJSON["branch_prefixes"]["features"]
fixBranches = configJSON["branch_prefixes"]["fixes"]
commitsMsgs = subprocess.getoutput("git log $(git branch --show-current)...origin/master --pretty=oneline --format='* %C(auto) %h %s'")
print("Git Log...\n" + commitsMsgs)
commitsLines = commitsMsgs.splitlines()
commitsLines[-1] = commitsLines[-1] + "\n"
fileContent = []
fileVars = []

if branchType in featBranches:
    branchType = "features"
elif branchType in fixBranches:
    branchType = "fixes"
else:
    branchType = "misc"
print("Git Branch type: " + branchType)

print("Identifying release notes variables...")
for arg in configJSON["env_variables"]:
    if arg == "{RELEASE_DATE}":
        fileVars.append(RELEASE_DATE)
    elif arg == "{GIT_REPO}":
        fileVars.append(GITHUB_REPO_PATH)
    elif arg == "{RELEASE_TAG}":
        fileVars.append(PRERELEASE_VERSION)

print("Creating release notes content...")
fileContent.append(configJSON["file_title"] + "\n")
for section in configJSON["sections"]:
    fileContent.append(section["header"] + "\n")
    if branchType == section["type"]:
        fileContent.extend(commitsLines)
    else:
        fileContent.append(section["default"] + "\n")

for footer in configJSON["footer_rows"]:
    fileContent.append(footer + "\n")
fileContent = [row + "\n" for row in fileContent]
releaseNotes = ''.join(fileContent)

for i, each in enumerate(configJSON["env_variables"]):
    releaseNotes = releaseNotes.replace(each, fileVars[i])

print("---------------------------------------------------------")
print("Release Notes Content")
print("---------------------------------------------------------")
print(releaseNotes)
print("---------------------------------------------------------")

print("Fiding Github Release with generated Tag....")
getReleaseURL = GITHUB_URL + "/repos/" + GITHUB_REPO_PATH + "/releases/tags/" + PRERELEASE_VERSION
getReleaseHeaders = {
  'Accept': 'application/vnd.github.v3+json',
  'Authorization': GITHUB_AUTH
}
getReleaseResp = requests.request("GET", getReleaseURL, headers=getReleaseHeaders)
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
patchReleaseHeaders = {
  'Accept': 'application/vnd.github.v3+json',
  'Authorization': GITHUB_AUTH,
  'Content-Type': 'application/json'
}

pathReleaseResp = requests.request("PATCH", patchReleaseURL, headers=patchReleaseHeaders, data=patchReleasePayload)
print("Path Request Status Code: " + str(pathReleaseResp.status_code))
if (pathReleaseResp.status_code == 200):
    print("GitHub Release Notes updated!!!")

