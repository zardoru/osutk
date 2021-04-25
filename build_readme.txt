Hi. This manual assumes you have some familiarity using command line tools. The $ denotes the shell, not a thing that you have to write into the command line.

Check Duplicate Hitsounds
===========================
To check if a map has duplicate hitsounds and you want to print them with timestamps:

$ check_duplicate_hitsounds.exe "path to your map yes with the quotes" -p > timestamps.txt

This will print them out to timestamps.txt.

To actually remove duplicates, use 

$ check_duplicate_hitsounds.exe "path to your map yes with the quotes" -d > objects.txt

And it will print the objects that need to replace your [HitObject] section onto objects.txt.

Make Hitsound Diff
===========================
This tool helps you create a hitsound difficulty from a normal difficulty. It sorts notes into distinct types of hitsounds so each hitsound has its own lane. Doesn't include full-auto hitsounds (i.e. notes with auto sampleset, auto index and hitsound normal).

Use it like this: 

$ make_hitsound_diff.exe "path to your map and yes with the quotes" > hsdiff.osu

This will output a new map that is a hitsound diff into hsdiff.osu.

This was built with osutk, which you can find here https://github.com/zardoru/osutk. The source code for it is under the tools/ folder.
Hope it's useful. - Agka