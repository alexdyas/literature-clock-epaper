#!/usr/bin/env python3
# ------------------------------------------------------------------------------
#
# Filename      - unicode-normaliser.py
#
# Description   - Convert all 'weird'unicode characters to their 'normal' ASCII
#                 equivalents
#                 More information - https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize
#
# Find me       - https://github.com/alexdyas/literature-clock-epaper/blob/main/tools/unicode-normaliser.py
#
# Usage         - cat <text file> | ./unicode-normaliser.py
#               - ./unicode-normaliser.py --file <text file>
#
# ------------------------------------------------------------------------------
import unicodedata
import sys
import optparse

filename = ""

if __name__ == "__main__":

    parser = optparse.OptionParser()
    parser.add_option("-f", "--file", dest="file")
    options, arguments = parser.parse_args()

    if options.file:
        filename = options.file
        filehandle = open(filename, "r")
    else:
        filehandle = sys.stdin

    while 1:
        char = filehandle.read(1)
        if not char:
            break
        if not unicodedata.is_normalized("NFKC", char):
            print(unicodedata.normalize("NFKC", char), end="")
        else:
            print(char, end="")
    filehandle.close()
