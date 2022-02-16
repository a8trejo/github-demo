import os
import json
import requests

GITHUB_URL = os.environ["GITHUB_URL"]
GITHUB_REPO_PATH = os.environ["GITHUB_REPO_PATH"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_AUTH = "Bearer " + GITHUB_TOKEN
README_URL = os.environ["README_URL"]
README_API_KEY = os.environ["README_API_KEY"]
API_DREAM_TEAM = os.environ["API_DREAM_TEAM"].replace(" ", "").split(",")

GITHUB_AUTH_HEADER = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": GITHUB_AUTH,
}
GITHUB_PAYLOAD_HEADER = {
    **GITHUB_AUTH_HEADER,
    "Content-Type": "application/json"
}
README_AUTH_HEADER = {
    "Authorization": "Basic " + README_API_KEY,
}
README_PAYLOAD_HEADER = {
    **README_AUTH_HEADER,
    "Content-Type": "application/json"
}
CONFIG_FILE = open(".github/changelog_config.json")
CONFIG_JSON = json.load(CONFIG_FILE)
CONFIG_FILE.close()
readme_sections = []
readme_synch = False

print("Finding Github Latest Release Contents....")
get_latest_release_url = GITHUB_URL + "/repos/" + GITHUB_REPO_PATH + "/releases/latest"
get_latest_release_resp = requests.request(
    "GET", get_latest_release_url, headers=GITHUB_AUTH_HEADER
)
print("Get Latest Release Status Code: " + str(get_latest_release_resp.status_code))

release_body = get_latest_release_resp.json().get("body").splitlines()
release_notes_content = []
for row in release_body:
    # Any release notes row unrelated to commit will be considered
    if "by (" not in row:
        release_notes_content.append(row)
    else:
        # Removing commit sha from the commits msgs
        parsed_row = row[2] + row[10:-1] + row[-1]

        # Only adding commits msgs belonging to API & Integrations team
        for team_member in API_DREAM_TEAM:
            if "by (" in row and team_member in row:
                release_notes_content.append(parsed_row)
                readme_synch = True
print("-------------------------------------------------------------------------------")
print("Latest Release Parsed Content")
print("-------------------------------------------------------------------------------")
print(release_notes_content)

# Will only synch with readme if there's content related to API & Integrations team
if readme_synch == True:

    #Removing author names from commits msgs
    release_notes_content = [row.split("by (")[0] for row in release_notes_content]
    release_notes_content = [row.split("by (")[0] for row in release_notes_content]

    #Getting the date of the release from the Github Tag
    release_notes_tag = get_latest_release_resp.json().get("tag_name")
    changelog_date = release_notes_tag[1:11]

    #Going through each section configured for the release notes to categorize within readme's types
    for i, section in enumerate(CONFIG_JSON["sections"]):
        row_start = release_notes_content.index(section["header"])
        row_end = len(CONFIG_JSON["sections"])-1 if i+1 == len(CONFIG_JSON["sections"]) else release_notes_content.index(CONFIG_JSON["sections"][i+1]["header"])
        readme_post = {}
        readme_post["text"] = release_notes_content[row_start:row_end]
        
        # Excluding release notes section with only default content
        if release_notes_content[ row_start + 2 ] != section["default"]:

            if section["type"] == "features":
                readme_post["type"] = "added"
                readme_sections.append(readme_post)
            elif section["type"] == "misc":
                if len(readme_sections) == 0:
                    readme_post["type"] = "added"
                    readme_sections.append(readme_post)
                else:
                    readme_sections[0]["text"] = readme_sections[0]["text"] + release_notes_content[row_start:row_end]

            elif section["type"] == "fixes":
                readme_post["type"] = "fixed"
                readme_sections.append(readme_post)

            elif section["type"] == "improved":
                readme_post["type"] = "improved"
                readme_sections.append(readme_post)

            elif section["type"] == "breaking":
                readme_post["type"] = "deprecated"
                readme_sections.append(readme_post)

            elif section["type"] == "depend":
                if readme_sections[-1]["type"] != "deprecated":
                    readme_post["type"] = "deprecated"
                    readme_sections.append(readme_post)
                else:
                    readme_sections[-1]["text"] = readme_sections[-1]["text"] + release_notes_content[row_start:row_end]

    if len(readme_sections) != 0:
        for entry in readme_sections:
            entry["text"] = [row + "\n" for row in entry["text"]]
            payload_text = "".join(entry["text"])
            readme_payload = json.dumps({
                "title": "Postscript API - " + changelog_date,
                "type": entry["type"],
                "body": payload_text,
                "hidden": True
            })
            print("-------------------------------------------------------------------------------")
            print("Creating Changelog Entry in readme as '" + entry["type"] + "'")
            print("-------------------------------------------------------------------------------")
            readmeResponse = requests.request("POST", README_URL, headers=README_PAYLOAD_HEADER, data=readme_payload)
            print(readmeResponse.text)
    else:
        print("Release Content does not have any header matching the sections in .github/prerelease_config.json file")
else:
    print("No commit was performed by the API & Integrations team")