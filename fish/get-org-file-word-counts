#!/usr/bin/fish

# sed ignores words longer than 25 characters

for file in **.org
  tr -d '[:punct:]' < "$file" | tr '[A-Z] ' '[a-z]\n' | sort -u
end | sed '/^.\{25\}./d'| grep -v -e "http" | sort | uniq -c | sort -g | tac
