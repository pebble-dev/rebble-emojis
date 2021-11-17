# This script dynamically generats a readme.md

output="$(cat autogen/readme_top.md)"

output="$output

# Current Emojis

"

for f in $(ls emoji); do
	output="${output}![](emoji/${f}) - ${f}
	   
	"
done

echo "$output">readme.md
