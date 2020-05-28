#!/usr/bin/fish

if not [ (math (count $argv)%2) -eq 0 ]
  echo "You need to have an even number of arguments"
  exit 1
end

set td (mktemp -d -t combine_images_XXXX)

for p in $argv
  convert -border 6x6 $p $td"/"$p
end

for i in (seq 1 2 (count $argv))
  set f1 $td"/"$argv[$i]
  set f2 $td"/"$argv[(math "$i + 1")]
  set out_path $td"/"$i.png
  convert $f1 $f2 +append $out_path
  set merged $merged $out_path
end

convert $merged -append final.png

rm -r $td
