#!/usr/bin/env python3

import os
import json
import glob
import shutil
from PIL import Image

outputs = [
  { "name": "emoji_14", "suffix": "sm", "size": 14, "top": 0 },
  { "name": "emoji_18", "suffix": "sm", "size": 18, "top": 2 },
  { "name": "emoji_24", "suffix": "lg", "size": 24, "top": 0 },
  { "name": "emoji_28", "suffix": "lg", "size": 28, "top": 2 }
]

if not os.path.exists("emoji.json"):
  print("You are in a wrong directory to build the fonts")
  quit()

os.makedirs("build", exist_ok=True)
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
  os.system("cd build && python2 ../pebble-firmware-utils/fontgen.py pfo %d %s %s.pfo --list %s.json && cd .." % (output['size'], suffix, output['name'], output["name"]))
  print("Generated build/%s.pfo" % output['name'])
  os.remove('build/%s.json' % output["name"])
for folder in ["sm", "lg"]:
  shutil.rmtree("build/%s" % folder)
