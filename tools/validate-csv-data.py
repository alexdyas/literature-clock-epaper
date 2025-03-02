#!/usr/bin/env python3
# ------------------------------------------------------------------------------
#
# Filename      - validate-csv-data.py
#
# Description   - Read in formatted CSV quotes file, check each line and report
#                 on any issues.  See below for the checks.
#
# Find me       - https://github.com/alexdyas/literature-clock-epaper/blob/main/tools/validate-csv-data.py
#
# Usage         - ./validate-csv-data.py --csvfile=csvfile.csv
#               - cat csvfile.csv | ./validate-csv-data.py
#
# Notes         - Logging
#                   - ERROR - A problem that will prevent the applicagtion from
#                             running or crash it
#                   - WARNING - A problem in the CSV file that that won't crash
#                               the application
#
# ------------------------------------------------------------------------------
import logging
import sys
import optparse
import csv

# Initialise
lasthour = 0
lastminute = 0
logging.basicConfig(level=logging.DEBUG)
count = 1


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
        count = count + 1
        try:
            digittime, texttime, snippet, title, author, sfw = row
        except ValueError:
            logging.error(
                f"Record {count} - doesn't have the requisit number of fields"
            )
            continue

        hour, minute = digittime.split(":")
        hour = int(hour)
        minute = int(minute)

        if hour < lasthour:
            logging.error(f"Record {count} - {hour} is out of sequence")

        if hour < 0 or hour > 23:
            logging.error(f"Record {count} - {hour} is impossible")

        if hour > (lasthour + 2):
            logging.warning(
                f"Record {count} - {hour} is more than an hour ahead of the previous record ({lasthour}), an hour missing"
            )

        if minute < 0 or minute > 59:
            logging.error(f"Record {count} - {minute} is impossible")

        if minute > lastminute + 1:
            logging.warning(
                f"Record {count} - {minute} is more than an minute ahead of the previous record ({str(minute).zfill(2)}), record missing for {str(hour).zfill(2)}:{str(minute-1).zfill(2)}"
            )

        if texttime == "":
            logging.warning(
                f"Record {count} - texttime field is empty for record {count}"
            )

        if snippet == "":
            logging.warning(
                f"Record {count} - snippet field is empty for record {count}"
            )

        if title == "":
            logging.warning(
                f"Record {count} - booktitle field is empty for record {count}"
            )

        if author == "":
            logging.warning(
                f"Record {count} - author field is empty for record {count}"
            )

        if sfw == "":
            logging.warning(f"Record {count} - sfw field is empty for record {count}")

        if snippet.find(texttime) == -1:
            logging.warning(f"Record {count} - timetext not found in snippet")

        lasthour = hour
        lastminute = minute

logging.info(f"Read {csvfilename}, processed {count} records")
