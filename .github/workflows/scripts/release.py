import os
import json
import subprocess
import requests

GITHUB_URL = os.environ["GITHUB_URL"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GIT_BRANCH = os.environ["GITHUB_BRANCH"]
GITHUB_REPO_PATH = os.environ["GITHUB_REPO_PATH"]
RELEASE_VERSION = os.environ["RELEASE_VERSION"]
RELEASE_DATE = os.environ["RELEASE_DATE"]
OLD_LATEST = os.environ["OLD_LATEST"]
GITHUB_AUTH = "Bearer " + GITHUB_TOKEN
GITHUB_GET_HEADER = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": GITHUB_AUTH,
}
GITHUB_PAYLOAD_HEADER = {
    **GITHUB_GET_HEADER,
    "Content-Type": "application/json",
}

#Debug read file in upper path
CONFIG_FILE = open('.github/changelog_config.json')
CONFIG_JSON = json.load(CONFIG_FILE)
CONFIG_FILE.close()
FEAT_PREFIXES = CONFIG_JSON["branch_prefixes"]["features"]
FIX_PREFIXES = CONFIG_JSON["branch_prefixes"]["fixes"]
notes_content = []
file_vars = []
source_branches = []
source_branches_type = []
release_notes = ""

print("GitHub Old 'Latest' Tag: " + OLD_LATEST)
print("---------------------------------------------------------")
# Fetching commit difference between tags with "git log" command
commits_msgs = subprocess.getoutput(
    "git log '"
    + OLD_LATEST
    + "'...'"
    + RELEASE_VERSION
    + "' --pretty=oneline --format='* %C(auto) %h %s by (%an)'"
)
commits_lines = commits_msgs.splitlines()

# Only generating the new release content IF there is actual difference between the new tag and latest
# If there's no commit diff between the new pre release and latest, just use the same content of the latest release
if len(commits_lines) != 0:
    commits_lines[-1] = commits_lines[-1] + "\n"
    print(
        "Git Log Diff between Latest Release("
        + OLD_LATEST
        + ") and "
        + RELEASE_VERSION
        + "...\n"
        + commits_msgs
    )
    print("---------------------------------------------------------")

    for commit in commits_lines:
        commit_sha = commit.split(" ")[2]
        # To see in which branches a commit resides, 'r' for remote, 'a' for local and remote, no flag for only local
        commit_branches = subprocess.getoutput(
            "git branch -r --contains "
            + commit_sha
            + " --sort=committerdate --format='%(refname:lstrip=-2)'"
        )
        commit_first_branch = commit_branches.splitlines()[0]
        source_branches.append(commit_first_branch)
        print("Commit " + commit_sha + " comes from branch: " + commit_first_branch)

    for branch in source_branches:
        branch_type = branch.split("/")[0].lower()
        if branch_type in FEAT_PREFIXES:
            branch_type = "features"
        elif branch_type in FIX_PREFIXES:
            branch_type = "fixes"
        else:
            branch_type = "misc"
        source_branches_type.append(branch_type)
        print("Git Branch " + branch + " -> type: " + branch_type)

    print("---------------------------------------------------------")
    print("Creating release notes content...")
    notes_content.append(CONFIG_JSON["file_title"] + "\n")

    for section in CONFIG_JSON["sections"]:
        notes_content.append(section["header"] + "\n")
        if section["type"] in source_branches_type:
            for i, commit_branch_type in enumerate(source_branches_type):
                if section["type"] == commit_branch_type:
                    notes_content.append(commits_lines[i])
        else:
            notes_content.append(section["default"] + "\n")

    for footer in CONFIG_JSON["footer_rows"]:
        notes_content.append(footer + "\n")

    notes_content = [row + "\n" for row in notes_content]
    release_notes = "".join(notes_content)

    print("Identifying release notes variables actual values...")
    for arg in CONFIG_JSON["env_variables"]:
        if arg == "{RELEASE_DATE}":
            file_vars.append(RELEASE_DATE)
        elif arg == "{GIT_REPO}":
            file_vars.append(GITHUB_REPO_PATH)
        elif arg == "{RELEASE_TAG}":
            file_vars.append(RELEASE_VERSION)

    for i, each in enumerate(CONFIG_JSON["env_variables"]):
        release_notes = release_notes.replace(each, file_vars[i])

    print("---------------------------------------------------------")
    print("Release Notes Content")
    print("---------------------------------------------------------")
    print(release_notes)
    print("---------------------------------------------------------")

    print("Finding Github Release with generated Tag....")
    get_release_url = (
        GITHUB_URL + "/repos/" + GITHUB_REPO_PATH + "/releases/tags/" + RELEASE_VERSION
    )
    get_release_resp = requests.request("GET", get_release_url, headers=GITHUB_GET_HEADER)
    print("Get Release Status Code: " + str(get_release_resp.status_code))
    release_id = get_release_resp.json().get("id")
    print("GitHub Release ID: " + str(release_id))
    print("---------------------------------------------------------")
    print("Patching GitHub Release with Release Notes content")
    patch_release_url = (
        GITHUB_URL + "/repos/" + GITHUB_REPO_PATH + "/releases/" + str(release_id)
    )
    patch_release_payload = json.dumps(
        {"tag_name": RELEASE_VERSION, "body": release_notes}
    )
    patch_release_resp = requests.request(
        "PATCH",
        patch_release_url,
        headers=GITHUB_PAYLOAD_HEADER,
        data=patch_release_payload,
    )
    print("Patch Request Status Code: " + str(patch_release_resp.status_code))
    if patch_release_resp.status_code == 200:
        print("GitHub Release Notes updated!!!")
    else:
        print(
            "Patch Release Notes failed!!!... manually open the release and edit its contents:\n"
        )

    print(
        "Release URL: https://github.com/"
        + GITHUB_REPO_PATH
        + "/releases/tag/"
        + RELEASE_VERSION
    )
else:
    print(f"There is no commit difference between tags {OLD_LATEST} (old latest) and {RELEASE_DATE}(new latest)!")