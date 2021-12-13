import json
import glob
import sys
import os
from PIL import Image

metrics_file = open("metrics.json")
metrics_json = json.load(metrics_file)

os.system('git remote add -f upstream https://github.com/pebble-dev/rebble-emojis.git')

diff = os.popen('git diff --cached --name-status upstream/master')

files = []
for line in diff.readlines():
  files.append(line.split()[-1])

for folder in ["sm", "lg"]:
  size = 14 if folder == "sm" else 24
  metrics = metrics_json["gothic_%d_emoji" % size]['glyphs']
  folder_files = glob.glob("emoji/*-%s.png" % folder)
  if files:
    folder_files = list(filter(lambda x: x in files, folder_files)) 
  for file in folder_files:
    codepoint = int(file[file.find('/')+1 : file.find('-')], 16)
    glyph = [d for d in metrics if d['codepoint'] == codepoint]
    if glyph:
      glyph = glyph[0]
      image = Image.open(file)
      width, height = image.size
      if width == glyph['width'] and height == glyph['height']:
        print("Glyph %s has the same size as the original gothic" % chr(codepoint))
      else:
        sys.exit("Glyph %s (%s) has wrong size (%dx%d) compared to original gothic (%dx%d)" % (chr(codepoint), file, width, height, glyph['width'], glyph['height']))
    else:
      print("Glyph %s wasn't a part of original gothic, ignoring metrics check" % chr(codepoint))

