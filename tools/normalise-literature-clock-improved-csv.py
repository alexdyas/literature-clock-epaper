#!/usr/bin/env python3
# ------------------------------------------------------------------------------
#
# Filename      - normalise-literature-clock-improved-csv.py
#
# Description   - Convert csv files from the literature-clock-improved to the
#                 format we need. Mainly means taking out the second column,
#                 and the title header row
#
# Find me       - https://github.com/alexdyas/literature-clock-epaper/blob/main/tools/normalise-literature-clock-improved-csv.py
#
# Usage         - cat quotes.en-US.csv | ./normalise-literature-clock-improved-csv.py
#               - ./normalise-literature-clock-improved-csv.py --csvfile quotes.en-US.csv
#
# ------------------------------------------------------------------------------
import optparse
import sys
import csv

FIELDDELIMETER = "|"

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

    csv_reader = csv.reader(filehandle, delimiter="|")
    for row in csv_reader:
        # Throw out header line
        if row[0] != "Time":
            # Remove second column we don't need
            del row[1]

            print(FIELDDELIMETER.join(row))

    filehandle.close()
