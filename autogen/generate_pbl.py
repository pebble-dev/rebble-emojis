#!/usr/bin/env python3

import os
import json
import glob
import shutil
import re
from PIL import Image

outputs = [
  { "name": "emoji_14", "suffix": "sm", "size": 14, "top": 0, "export": ["001", "002"] },
  { "name": "emoji_18", "suffix": "sm", "size": 18, "top": 2, "export": ["003", "004"] },
  { "name": "emoji_24", "suffix": "lg", "size": 24, "top": 0, "export": ["005", "006"] },
  { "name": "emoji_28", "suffix": "lg", "size": 28, "top": 2, "export": ["007", "008"] }
]

if os.path.exists("emoji.json"):
  os.makedirs("build", exist_ok=True)
  os.system("cd build && git clone https://github.com/MarSoft/pebble-firmware-utils.git && cd ..")
  emojis_file = open("emoji.json")
  emojis_json = json.load(emojis_file)
  for folder in ["sm", "lg"]:
    files = glob.glob("emoji/*-%s.png" % folder)
    os.makedirs("build/%s" % folder, exist_ok=True)
    for file in files:
      shutil.copyfile(file, "build/%s/%05X.png" % (folder, int(file[file.find('/')+1 : file.find('-')], 16)))
  for output in outputs:
    output_json = {}
    output_json['metadata'] = []
    suffix = output["suffix"]
    for emoji in emojis_json:
      image = Image.open("build/%s/%05X.png" % (suffix, ord(emoji["character"])))
      metrics = emoji[suffix]
      width, height = image.size
      output_json['metadata'].append({
        'codepoint': ord(emoji["character"]),
        'advance': width + 2, # 1 padding on left and right side
        'top': metrics["top"] + output["top"],
        'left': 1
      })
    with open('build/%s.json' % output["name"], 'w') as f:
      json.dump(output_json, f)
    os.system("cd build && python2 pebble-firmware-utils/fontgen.py pfo %d %s %s.pfo --list %s.json && cd .." % (output['size'], suffix, output['name'], output["name"]))
    os.makedirs("build/resources", exist_ok=True)
    for export in output["export"]:
      shutil.copyfile("build/%s.pfo" % output["name"], "build/resources/%s" % export)
    os.remove("build/%s.pfo" % output["name"])
    if not os.path.exists("build/resources/000"):
      os.mknod("build/resources/000")
    for n in range(10):
      filepath = "build/resources/%03d" % (n + 9)
      if not os.path.exists(filepath):
        os.mknod(filepath)
    os.system("cd build && python2 pebble-firmware-utils/pbpack.py resources/ emoji.pbl && cd ..")
else:
  print("You are in a wrong directory to build the fonts")
