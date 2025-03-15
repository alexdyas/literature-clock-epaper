#!/usr/bin/env python3
# ------------------------------------------------------------------------------
#
# File          - clean-csv-data.py
#
# Description   - Clean CSV quotes file of various errors and incompatibilities.
#                 This is typically used when importing data from other similar projects
#
# Find me       - https://github.com/alexdyas/literature-clock-epaper/blob/main/tools/clean-csv-data.py
#
# Usage         - ./clean-csv-data.py <csv file>
#               - cat <csv file> | ./clean-csv-data.py
#
# Notes         - See comments for details of changes
#               - Assumed to be a valid CSV file
#
# ------------------------------------------------------------------------------
import optparse
import sys
import csv
import re

if __name__ == "__main__":
    csvfilename = ""
    parser = optparse.OptionParser()
    parser.add_option("-f", "--csvfile", dest="csvfile")
    options, arguments = parser.parse_args()

    if options.csvfile:
        csvfilename = options.csvfile
        filehandle = open(csvfilename, "r")
    else:
        filehandle = sys.stdin

    # Changes
    for line in filehandle:
        # If we can't find the texttime in the snippet try uppercasing the first
        # letter of the texttime, or then lowercasing.
        [time, texttime, snippet, title, author, sfw] = line.split("|")
        if snippet.find(texttime) == -1:
            if snippet.find(texttime.capitalize()) != -1:
                line = "|".join(
                    [time, texttime.capitalize(), snippet, title, author, sfw]
                )
            elif snippet.find(texttime.lower()) != -1:
                line = "|".join([time, texttime.lower(), snippet, title, author, sfw])
        # Standardise quote characters
        line = re.sub(r"’", "'", line)
        line = re.sub(r"‘", "'", line)
        line = re.sub(r"“", '"', line)
        line = re.sub(r"”", '"', line)
        # Standardise dashes
        line = re.sub(r"—", "-", line)
        # Standardise dots
        line = re.sub(r"…", "...", line)
        line = re.sub(r"\. \. \.", "...", line)
        # Standardise breaks
        line = re.sub(r"<br\/>", "<br>", line)
        line = re.sub(r"<br> ", "<br>", line)
        line = re.sub(r" <br>", "<br>", line)
        line = re.sub(r"<br \/>", "<br>", line)
        # Remove emphasis quotes that we don't support
        line = re.sub(r"<em>", "", line)
        line = re.sub(r"<\/em>", "", line)
        # Convert fake carriage returns
        line = re.sub(r"\\n", "<br>", line)
        # Useless spaces
        line = re.sub(r" \|", "|", line)
        line = re.sub(r"\| ", "|", line)
        # Remove quotes from texttime field
        [time, texttime, snippet, title, author, sfw] = line.split("|")
        texttime = re.sub(r'"', "", texttime)
        line = "|".join([time, texttime, snippet, title, author, sfw])

        print(line, end="")

    filehandle.close()
