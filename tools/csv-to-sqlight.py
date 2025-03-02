#!/usr/bin/env python3
# ------------------------------------------------------------------------------
#
# Filename      - csv-to-sqlight.py
#
# Description   - Take Literature Clock CSV file and create a SQLight Database
#                 of the records
#
# Find me       - https://github.com/alexdyas/literature-clock-epaper/blob/main/tools/csv-to-sqlight.py
#
# Usage         - ./csv-to-sqlight.py --csvfile=<csv file> --sqlightdb=<sqllightdb file>
#               - cat <csv file> | ./csv-to-sqlight.py --sqlightdb=<sqllightdb file>
#
# ------------------------------------------------------------------------------
import logging
import sqlite3
from os.path import exists
import sys
import optparse
import csv


def quote_field(text):
    """Quote double quotes for insertion into SQLight database"""
    return text.replace('"', '""')


# - Initialise -----------------------------------------------------------------
logging.basicConfig(level=logging.DEBUG)
count = 0
sql_create_table = """
      CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY,
            digittime text NOT NULL,
            texttime text NOT NULL,
            snippet text NOT NULL,
            title text NOT NULL,
            author text NOT NULL,
            sfw text NOT NULL
        ) STRICT;"""

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-f", "--csvfile", dest="csvfile")
    parser.add_option("-s", "--sqlightdb", dest="sqlightdb")
    options, arguments = parser.parse_args()

    # - Pre-flight checks ----------------------------------------------------------
    if options.csvfile:
        csvfilename = options.csvfile
        filehandle = open(csvfilename, "r")
    else:
        filehandle = sys.stdin

    if options.sqlightdb:
        sqlightdbfilename = options.sqlightdb
    if exists(sqlightdbfilename):
        logging.error(f"Database {sqlightdbfilename} already exists, quitting")
        exit(1)

    # - Main -----------------------------------------------------------------------
    try:
        with sqlite3.connect(sqlightdbfilename) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_create_table)
            conn.commit()

            csv_reader = csv.reader(filehandle, delimiter="|")
            for row in csv_reader:
                digittime, texttime, snippet, title, author, sfw = row
                snippet = quote_field(snippet)
                title = quote_field(title)
                author = quote_field(author)
                sql_insert = f"""INSERT INTO quotes(digittime,texttime,snippet,title,author,sfw) VALUES("{digittime}","{texttime}","{snippet}","{title}","{author}","{sfw}")"""
                cursor.execute(sql_insert)
                count = count + 1
    except sqlite3.OperationalError as e:
        logging.error(f"Failed to open database:" + e)
        exit(1)

    logging.info(f"Written {sqlightdbfilename}, processed {count} records")
    conn.close()
