import os

GITHUB_REPO_PATH = os.environ['GITHUB_REPO_PATH']
GITHUB_OUTPUT = os.getenv('GITHUB_OUTPUT')

print("--------------------Fetching Commit Msg-------------------------------------")
commitMsg = 'Revert "- ATH-8 BB Haqwert Pabcde (as sd asads)" \'ab1gbh0\' Git-Demo"'
print(commitMsg)

# Removing special characters from the commit msg
specialChars = [',', "'", '"', '(', ')']
for char in specialChars:
    if char in commitMsg:
        commitMsg = commitMsg.replace(char, '')

# Parsing repo name from repo path
repoName = GITHUB_REPO_PATH.split('/')[1]

print(f"parsed-msg={commitMsg} {repoName}")
# Writing Github Job Output Variable with the complete msg to send to cypress cloud
with open(GITHUB_OUTPUT, "a") as jobOutputs:
    jobOutputs.write(f"parsed-msg={commitMsg} {repoName}")
