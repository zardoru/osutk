Hi. This manual assumes you have some familiarity using command line tools.

To check if a map has duplicate hitsounds and you want to print them with timestamps:

check_duplicate_hitsounds.exe "path to your map yes with the quotes" -p > timestamps.txt

This will print them out to timestamps.txt.

To actually remove duplicates, use 

check_duplicate_hitsounds.exe "path to your map yes with the quotes" -d > objects.txt

And it will print the objects that need to replace your [HitObject] section.

This was built with osutk, which you can find here https://github.com/zardoru/osutk. The source code for it is under the tools/ folder.
Hope it's useful. - Agka