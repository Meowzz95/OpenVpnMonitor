import json
import os
cwd = os.getcwd()
print("Current directory %s"%cwd)

config = None
with open("Config.json") as fp:
    config = json.load(fp)
