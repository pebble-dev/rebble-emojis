#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

import os
import sys
import json
import unicodedata

try:
    from PIL import Image, ImageChops
except ImportError:
    print("Error: Pillow is required to generate preview images.")
    print("Please install it: pip install pillow")
    sys.exit(1)

def is_printable_and_non_pua(cp):
    # PUA ranges:
    # U+E000 to U+F8FF
    # U+F0000 to U+FFFFD
    # U+100000 to U+10FFFD
    if 0xE000 <= cp <= 0xF8FF:
        return False
    if 0xF0000 <= cp <= 0xFFFFD:
        return False
    if 0x100000 <= cp <= 0x10FFFD:
        return False
    
    # Check category
    category = unicodedata.category(chr(cp))
    if category.startswith('C'): # Control, Format, Surrogate, Private Use, Unassigned
        return False
    return True

def get_char_name(cp):
    try:
        char = chr(cp)
        name = unicodedata.name(char)
        return name.title()
    except ValueError:
        return f"Custom Emoji (U+{cp:04X})"

def save_if_different(dest_img, dest_path):
    if os.path.exists(dest_path):
        try:
            with Image.open(dest_path) as existing_img:
                if existing_img.size == dest_img.size:
                    existing_rgba = existing_img.convert("RGBA") if existing_img.mode != "RGBA" else existing_img
                    diff = ImageChops.difference(existing_rgba, dest_img)
                    if diff.getbbox() is None:
                        return False
        except Exception:
            pass
    dest_img.save(dest_path)
    return True

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    emoji18_dir = os.path.join(base_dir, "src", "emoji18")
    emoji24_dir = os.path.join(base_dir, "src", "emoji24")
    preview_dir = os.path.join(base_dir, "build", "preview")
    
    # Create preview directories
    preview18_dir = os.path.join(preview_dir, "18")
    preview24_dir = os.path.join(preview_dir, "24")
    os.makedirs(preview18_dir, exist_ok=True)
    os.makedirs(preview24_dir, exist_ok=True)
    
    # Load manifests
    manifest18_path = os.path.join(emoji18_dir, "font.json")
    manifest24_path = os.path.join(emoji24_dir, "font.json")
    
    if not os.path.exists(manifest18_path) or not os.path.exists(manifest24_path):
        print("Error: manifests not found.")
        return 1
        
    with open(manifest18_path, "r") as f:
        manifest18 = json.load(f)
    with open(manifest24_path, "r") as f:
        manifest24 = json.load(f)
        
    # Build dictionary of glyphs by codepoint
    glyphs18 = {g["codepoint"]: g for g in manifest18["glyphs"]}
    glyphs24 = {g["codepoint"]: g for g in manifest24["glyphs"]}
    
    # Get all unique codepoints
    all_cps = sorted(list(set(glyphs18.keys()) | set(glyphs24.keys())))
    
    # Generate previews
    print("Generating preview images...")
    processed_count = 0
    for cp in all_cps:
        # Process 18px glyph
        if cp in glyphs18:
            g = glyphs18[cp]
            if g.get("width", 0) > 0 and g.get("height", 0) > 0:
                src_path = os.path.join(emoji18_dir, g["file"])
                if os.path.exists(src_path):
                    dest_path = os.path.join(preview18_dir, os.path.basename(g["file"]))
                    try:
                        img = Image.open(src_path).convert('L')
                        dest_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
                        dest_img.putalpha(img)
                        save_if_different(dest_img, dest_path)
                        processed_count += 1
                    except Exception as e:
                        print(f"Warning: failed to process {src_path}: {e}")
                        
        # Process 24px glyph
        if cp in glyphs24:
            g = glyphs24[cp]
            if g.get("width", 0) > 0 and g.get("height", 0) > 0:
                src_path = os.path.join(emoji24_dir, g["file"])
                if os.path.exists(src_path):
                    dest_path = os.path.join(preview24_dir, os.path.basename(g["file"]))
                    try:
                        img = Image.open(src_path).convert('L')
                        dest_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
                        dest_img.putalpha(img)
                        save_if_different(dest_img, dest_path)
                        processed_count += 1
                    except Exception as e:
                        print(f"Warning: failed to process {src_path}: {e}")
                        
    print(f"Generated {processed_count} preview images.")
    
    # Generate Markdown table
    table_lines = [
        "| Codepoint | Emoji | Name | Small (18px) | Large (24px) |",
        "| :--- | :---: | :--- | :---: | :---: |"
    ]
    
    for cp in all_cps:
        hex_str = f"U+{cp:04X}"
        char_val = chr(cp)
        char_disp = char_val if is_printable_and_non_pua(cp) else " "
        name_disp = get_char_name(cp)
        
        # 18px preview link
        p18_link = "-"
        if cp in glyphs18:
            g = glyphs18[cp]
            if g.get("width", 0) > 0 and g.get("height", 0) > 0:
                file_name = os.path.basename(g["file"])
                p18_link = f"![{hex_str} 18px](build/preview/18/{file_name})"
                
        # 24px preview link
        p24_link = "-"
        if cp in glyphs24:
            g = glyphs24[cp]
            if g.get("width", 0) > 0 and g.get("height", 0) > 0:
                file_name = os.path.basename(g["file"])
                p24_link = f"![{hex_str} 24px](build/preview/24/{file_name})"
                
        table_lines.append(f"| {hex_str} | {char_disp} | {name_disp} | {p18_link} | {p24_link} |")
        
    table_content = "\n".join(table_lines)
    
    # Read README.md and update it
    readme_path = os.path.join(base_dir, "README.md")
    
    start_marker = "<!-- EMOJI_TABLE_START -->"
    end_marker = "<!-- EMOJI_TABLE_END -->"
    
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = "# Rebble Emojis\n"
        
    if start_marker in content and end_marker in content:
        # Replace content between markers
        start_idx = content.find(start_marker) + len(start_marker)
        end_idx = content.find(end_marker)
        new_content = content[:start_idx] + "\n\n" + table_content + "\n\n" + content[end_idx:]
    else:
        # Append markers and content to the end
        new_content = content.rstrip() + f"\n\n{start_marker}\n\n## Emoji Table\n\n{table_content}\n\n{end_marker}\n"
        
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    print(f"Updated README.md with emoji table.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
