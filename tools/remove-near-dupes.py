#!/usr/bin/env python3
# ------------------------------------------------------------------------------
#
# Filename      - remove-near-dupes.py
#
# Description   - Removes lines from input file that are very similar or
#                 identical to the following line
#
# Find me       - https://github.com/alexdyas/literature-clock-epaper/blob/main/tools/remove-near-dupes.py
#
# Notes         - Assumes file has been sorted eg `sort <text file>`
#                 Hard coded difference ratio
#
# Usage         - cat <text file> | ./remove-near-dupes.py
#               - ./remove-near-dupes.py  --file <text file>
#
# ------------------------------------------------------------------------------
from difflib import SequenceMatcher
import sys
import os
import optparse

diffratio = 0.7
filename = ""


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


if __name__ == "__main__":

    parser = optparse.OptionParser()
    parser.add_option("-f", "--file", dest="file")
    options, arguments = parser.parse_args()

    if options.file:
        filename = options.file
        filehandle = open(filename, "r")
    else:
        filehandle = sys.stdin

    lastline = ""
    for line in filehandle:
        line = line.rstrip()
        if not similar(lastline, line) >= diffratio:
            print(line)
            lastline = line

    filehandle.close()
