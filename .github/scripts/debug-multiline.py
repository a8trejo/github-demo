import os

GITHUB_ENV = os.getenv('GITHUB_ENV')
MULTILINE_STRING = ":loud_sound: Woo-Hoo :loud_sound: ANALYSIS SUCCESSFUL, 1 more details at: ***/dashboard?\n*Security Hotspots on New Code*: :warning: 0\n*Maintainability Rating on New Code: OK* :cat-on-keyboard: Code Smells: 0\n*Reliability Rating on New Code: OK* :bug: Bugs: 0\n*Security Rating on New Code: OK* :unlock: Vulnerabilities: 0\n"

print(MULTILINE_STRING)
with open(GITHUB_ENV, "a") as env_file:
    env_file.write(f"VAR_NAME<<EOF\n{MULTILINE_STRING}EOF")