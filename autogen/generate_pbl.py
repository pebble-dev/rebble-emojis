#!/usr/bin/env python3

import os
import shutil

outputs = [
  { "name": "emoji_14", "export": ["001", "002"] },
  { "name": "emoji_18", "export": ["003", "004"] },
  { "name": "emoji_24", "export": ["005", "006"] },
  { "name": "emoji_28", "export": ["007", "008"] }
]

for output in outputs:
  if not os.path.exists("build/%s.pfo" % output["name"]):
    print("You are in a wrong directory to build the pbl. build/%s.pfo is missing" % output["name"])
    quit()

os.makedirs("build/resources/", exist_ok=True)
for output in outputs:
  for export in output["export"]:
    shutil.copyfile("build/%s.pfo" % output["name"], "build/resources/%s" % export)
if not os.path.exists("build/resources/000"):
  os.mknod("build/resources/000")
for n in range(10):
  filepath = "build/resources/%03d" % (n + 9)
  if not os.path.exists(filepath):
    os.mknod(filepath)
os.system("cd build && python2 ../pebble-firmware-utils/pbpack.py resources/ emoji.pbl && cd ..")
print("Generated build/emoji.pbl")
shutil.rmtree("build/resources/")
