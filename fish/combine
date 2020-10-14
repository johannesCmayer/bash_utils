#!/usr/bin/fish

argparse 'b/border=' 'o/out=' -- $argv

if not set -q _flag_border
  set _flag_border 2x2
end

if not set -q _flag_out
  set _flag_out final.png
end

if not [ (math (count $argv)%2) -eq 0 ]
  echo "You need to have an even number of arguments"
  exit 1
end

set td (mktemp -d -t combine_images_XXXXXX)

for p in $argv
  convert -border $_flag_border $p $td"/"$p
end

for i in (seq 1 2 (count $argv))
  set -l f1 $td"/"$argv[$i]
  set -l f2 $td"/"$argv[(math "$i + 1")]
  set -l out_path $td"/"$i.png
  convert $f1 $f2 +append $out_path
  set merged $merged $out_path
end

convert $merged -append $_flag_out

rm -r $td
