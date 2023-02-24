import os

GITHUB_REPO_PATH = os.environ['GITHUB_REPO_PATH']
GITHUB_OUTPUT = os.getenv('GITHUB_OUTPUT')

# Revert "- HSP-8 IC Contract Parity (Rest of Current Users)" ae5ccd2 Roo-Node"
# - HSP-637 paused hospital's posted shifts not visible to vets/techs 0369193 Roo-Node
print("--------------------Fetching Commit Msg-------------------------------------")
commitMsg = 'Revert "- ATH-8 BB Haqwert Pabcde (as sd asads)" \'ab1gbh0\' Git-Demo"'
print(commitMsg)
commitMsg = commitMsg.replace("'", '"', '(', ')')

# Removing special characters from the commit msg
specialChars = [',', "'", '"', '(', ')']
for char in specialChars:
    if char in commitMsg:
        commitMsg = commitMsg.replace(char, '')

# Removing RooVetGit from RooVetGit/Roo-Node (or respective repo name)
repoName = GITHUB_REPO_PATH.split('/')[1]

print(f"parsed-msg={commitMsg} {repoName}")
# Writing Github Job Output Variable with the complete msg to send to cypress cloud
with open(GITHUB_OUTPUT, "a") as jobOutputs:
    jobOutputs.write(f"parsed-msg={commitMsg} {repoName}")
