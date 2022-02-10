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
    if "by (" not in row:
        release_notes_content.append(row)
    else:
        for team_member in API_DREAM_TEAM:
            if "by (" in row and team_member in row:
                release_notes_content.append(row)
                readme_synch = True

print(release_notes_content)
if readme_synch == True:
    release_notes_content = [row.split("by (")[0] for row in release_notes_content]
    release_notes_content = [row.split("by (")[0] for row in release_notes_content]

    release_notes_tag = get_latest_release_resp.json().get("tag_name")
    changelog_date = release_notes_tag[1:11]

    for i, section in enumerate(CONFIG_JSON["sections"]):
        row_start = release_notes_content.index(section["header"])
        row_end = len(CONFIG_JSON["sections"])-1 if i+1 == len(CONFIG_JSON["sections"]) else release_notes_content.index(CONFIG_JSON["sections"][i+1]["header"])
        readme_obj = {}
        readme_obj["text"] = release_notes_content[row_start:row_end]
        if release_notes_content[ row_start + 2 ] != section["default"]:

            if section["type"] == "features":
                readme_obj["type"] = "added"
                readme_sections.append(readme_obj)
            elif section["type"] == "misc":
                if len(readme_sections) == 0:
                    readme_obj["type"] = "added"
                    readme_sections.append(readme_obj)
                else:
                    readme_sections[0]["text"] = readme_sections[0]["text"] + release_notes_content[row_start:row_end]

            elif section["type"] == "fixes":
                readme_obj["type"] = "fixed"
                readme_sections.append(readme_obj)

            elif section["type"] == "improved":
                readme_obj["type"] = "improved"
                readme_sections.append(readme_obj)

            elif section["type"] == "breaking":
                readme_obj["type"] = "deprecated"
                readme_sections.append(readme_obj)

            elif section["type"] == "depend":
                if readme_sections[-1]["type"] != "deprecated":
                    readme_obj["type"] = "deprecated"
                    readme_sections.append(readme_obj)
                else:
                    readme_sections[-1]["text"] = readme_sections[-1]["text"] + release_notes_content[row_start:row_end]

    for entry in readme_sections:
        entry["text"] = [row + "\n" for row in entry["text"]]
        payload_text = "".join(entry["text"])
        readme_payload = json.dumps({
            "title": "Postscript API - " + changelog_date,
            "type": entry["type"],
            "body": payload_text,
            "hidden": True
        })
        print("---------------------Creating Changelog Entry in readme-------------------------------------------")
        readmeResponse = requests.request("POST", README_URL, headers=README_PAYLOAD_HEADER, data=readme_payload)
        print(readmeResponse.text)
else:
    print("No commit was performed by the API & Integrations team")
    
    
