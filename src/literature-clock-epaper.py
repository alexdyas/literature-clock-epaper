#!/usr/bin/env python3
# ------------------------------------------------------------------------------
#
# Filename    - literature-clock-epaper.py
#
# Description - Main application script
#
# Find me     - https://github.com/alexdyas/literature-clock-epaper/blob/main/tools/literature-clock-epaper.py
#
# Usage       - See ./literature-clock-epaper.py --help
#
# ------------------------------------------------------------------------------
import sys
import os

picdir = "pic/"
libdir = "lib/"
if os.path.exists(libdir):
    sys.path.append(libdir)

import optparse
import sqlite3
import logging
from waveshare_epd import epd3in7
import time
from datetime import datetime
import random
from PIL import Image, ImageDraw, ImageFont
import traceback
import textwrap
import socket
import subprocess


PROGRAM_NAME = "literature-clock-epaper"
PROGRAM_VERSION = "1.0.0"
ENCODING_CHARACTER = "_"
SMALL_FONT_LINE_WIDTH = 65
NORMAL_FONT_LINE_WIDTH = 50
NORMAL_FONT_MAX_LINES = 13
LOGGINGLEVEL = logging.INFO
DBFILENAME = "data/quotes.db"
SQL_QUOTES_TABLE = "quotes"
PAUSE_BETWEEN_QUOTES = 60
SMALL_REGULAR_FONT_16 = ImageFont.truetype(
    os.path.join(picdir, "Spectral-Regular.ttf"), 16
)
SMALL_BOLD_FONT_16 = ImageFont.truetype(os.path.join(picdir, "Spectral-Bold.ttf"), 16)
NORMAL_REGULAR_FONT_20 = ImageFont.truetype(
    os.path.join(picdir, "Spectral-Regular.ttf"), 20
)
NORMAL_BOLD_FONT_20 = ImageFont.truetype(os.path.join(picdir, "Spectral-Bold.ttf"), 20)
TEXTLINESVERTICALOFFSET = 20


def clean_snippet(snippet):
    """Any cleanup that needs to be done to the snippet before processing"""
    # Make all <br>s the same
    snippet = snippet.replace("<br/>", "<br>")
    return snippet


def split_and_encode_bold(haystacktext, needletext, linelength):
    """Takes a line of text, splits it into linelength chunks, encodes thebold piece.
    Assumes only one thebold match in thetext. Bold encoding is wrapping between
    _ characters, so these must not exist in thetext"""

    # We can't deal with strings that already have the encoding character in them
    if haystacktext.find(ENCODING_CHARACTER) != -1:
        logging.debug(
            f"Quote text contains encoding character ({ENCODING_CHARACTER}), ignoring"
        )
        haystacktext = "Error, failed to read this record, sorry"
        needletext = "Error"

    haystacktext = clean_snippet(haystacktext)

    # Breakinto separate lines on hardcoded <br> tags
    # Note - We are assuming that the time is never divided across <br> tags
    # because that would be silly
    linelist = haystacktext.split("<br>")

    newlinelist = []
    for piece in linelist:
        # Encode the bold text. We only do this once, even if there are multiple
        # instances, because that's what I decided
        piece = piece.replace(needletext, "_" + needletext + "_", 1)
        piecelist = textwrap.wrap(
            piece,
            width=linelength,
            initial_indent="",
            subsequent_indent="",
            expand_tabs=True,
            replace_whitespace=True,
            fix_sentence_endings=False,
            break_long_words=True,
            drop_whitespace=True,
            break_on_hyphens=True,
            tabsize=8,
            max_lines=None,
            placeholder=" [...]",
        )
        for temppiece in piecelist:
            newlinelist.append(temppiece)

    # If we have any bold text crossing line endings, encode them individually
    for linenumber in range(len(newlinelist)):
        if (
            newlinelist[linenumber].count(ENCODING_CHARACTER) == 1
            and linenumber != len(newlinelist) - 1
        ):
            if newlinelist[linenumber + 1].count(ENCODING_CHARACTER) == 1:
                newlinelist[linenumber] = newlinelist[linenumber] + ENCODING_CHARACTER
                newlinelist[linenumber + 1] = (
                    ENCODING_CHARACTER + newlinelist[linenumber + 1]
                )

    return newlinelist


def read_random_snippet(hour, minute):
    """Reads book snippet from the database, returns:
    ["<Text of time>","<Snippet>","<Book title>","<Author>"]
    digittime, texttime, snippet, title, author, sfw
    """

    if not os.path.exists(DBFILENAME):
        logging.error(f"Database {DBFILENAME} doesn't exist, quitting")
        exit(1)

    try:
        with sqlite3.connect(DBFILENAME) as connection:
            cursor = connection.cursor()
    except sqlite3.OperationalError as e:
        logging.error(f"Failed to connect to SQLLight DB {DBFILENAME}, error {e}")
        return [
            "Error",
            "Error connecting to database, see logs.",
            "<no title>",
            "<nobody>",
        ]

    try:
        cursor.execute(
            f"SELECT * FROM {SQL_QUOTES_TABLE} WHERE digittime = '{hour}:{minute}' ORDER BY RANDOM() LIMIT 1;"
        )
        connection.commit()
        rows = cursor.fetchall()
    except Exception as e:
        logging.error(f"Failed to get row from SQLLight DB {DBFILENAME}, error {e}")
        return [
            "Error",
            "Error retrieving row from database, see logs.",
            "<no title>",
            "<nobody>",
        ]

    connection.close()

    # If there was no record return a message and carry on without crashing
    if len(rows) == 0 or len(rows[0]) < 7:
        rows = []
        rows.append([])
        rows[0].append("")
        rows[0].append("")
        rows[0].append(f"{hour}:{minute}")
        rows[0].append(f"No quote found for the time {hour}:{minute}, soz")
        rows[0].append(f"Best Seller")
        rows[0].append(f"Jane Doe")

    return [rows[0][2], rows[0][3], rows[0][4], rows[0][5]]


def get_ip():
    """Get and return the machines 'main' IP address"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(("10.254.254.254", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


def get_wifi_sid():
    """Get and return the WiFi SID. This process is not perfect, especially with mulptiple IP addresses, but it will do."""
    subprocess_result = subprocess.Popen("iwgetid", shell=True, stdout=subprocess.PIPE)
    subprocess_output = subprocess_result.communicate()[0], subprocess_result.returncode
    try:
        network_name = subprocess_output[0].decode("utf-8").split('"')[1]
    except IndexError:
        network_name = "<no wifi network found>"
    return network_name


def current_hour_minute_padded_string():
    """Returns tuple, [hour,minute] left zero padded strings"""
    current_time = datetime.now()
    return [str(current_time.hour).zfill(2), str(current_time.minute).zfill(2)]


def display_startup_information():
    """Display some information about this system and the application. Typically called at startup"""
    epd.init(0)
    epd.Clear(0xFF, 0)
    Himage = Image.new("1", (epd.height, epd.width), 0xFF)
    draw = ImageDraw.Draw(Himage)
    draw.text((0, 0), PROGRAM_NAME, font=NORMAL_REGULAR_FONT_20, fill=0)
    draw.text(
        (0, 20), f"Version - {PROGRAM_VERSION}", font=NORMAL_REGULAR_FONT_20, fill=0
    )
    draw.text(
        (0, 40), f"WiFi SID - {get_wifi_sid()}", font=NORMAL_REGULAR_FONT_20, fill=0
    )
    draw.text((0, 60), f"IP address - {get_ip()}", font=NORMAL_REGULAR_FONT_20, fill=0)
    draw.text((0, 80), f"DB file - {DBFILENAME}", font=NORMAL_REGULAR_FONT_20, fill=0)
    draw.text(
        (0, 100), f"Logging level - {LOGGINGLEVEL}", font=NORMAL_REGULAR_FONT_20, fill=0
    )
    draw.text(
        (0, 120),
        f"Regular font - {NORMAL_REGULAR_FONT_20.getname()}",
        font=NORMAL_REGULAR_FONT_20,
        fill=0,
    )
    draw.text(
        (0, 140),
        f"Bold font - {NORMAL_BOLD_FONT_20.getname()}",
        font=NORMAL_BOLD_FONT_20,
        fill=0,
    )
    [hour, minute] = current_hour_minute_padded_string()
    draw.text(
        (0, 160), f"Time at boot - {hour}:{minute}", font=NORMAL_REGULAR_FONT_20, fill=0
    )
    if options.FLIPSCREEN:
        Himage = Himage.transpose(Image.FLIP_TOP_BOTTOM)
        Himage = Himage.transpose(Image.FLIP_LEFT_RIGHT)
    epd.display_1Gray(epd.getbuffer(Himage))
    time.sleep(10)


# - Main -----------------------------------------------------------------------
if __name__ == "__main__":

    # - Command line options -------------------------------------------------------
    parser = optparse.OptionParser()
    parser.add_option(
        "-d",
        "--debug",
        action="store_true",
        dest="DEBUG",
        help="Output debug messages to console",
    )
    parser.add_option(
        "-f",
        "--flip",
        action="store_true",
        dest="FLIPSCREEN",
        help="Flip screen horizonally, and vertically",
    )
    parser.add_option(
        "-n",
        "--disableinfo",
        action="store_true",
        dest="DISABLEINFO",
        help="Do not display information on e-paper at start",
    )
    parser.add_option(
        "-o",
        "--oneofftime",
        dest="ONEOFFTIME",
        help="Run once, for supplied the hours:minutes, then stop",
    )
    parser.add_option(
        "-s",
        "--sqlightdbfile",
        dest="DBFILENAME",
        help=f"Path to SQLight DB file, default {DBFILENAME}",
    )
    options, arguments = parser.parse_args()

    if options.DEBUG:
        LOGGINGLEVEL = logging.DEBUG
    logging.basicConfig(
        level=LOGGINGLEVEL,
    )

    if options.DBFILENAME:
        DBFILENAME = options.DBFILENAME

    # - Initialise the e-paper screen --------------------------------------------------
    try:
        epd = epd3in7.EPD()
        logging.debug("Init and Clear")
    except IOError as e:
        logging.debug(e)
    except KeyboardInterrupt:
        logging.debug("ctrl + c:")
        epd3in7.epdconfig.module_exit(cleanup=True)
        exit(1)

    # ToDo - Put this in a function
    # - Display some interesting stuff on startup ------------------------------
    if not options.DISABLEINFO:
        display_startup_information()

    # - Main loop --------------------------------------------------------------
    while True:

        # Init e-paper screen
        epd.init(0)
        epd.Clear(0xFF, 0)
        Himage = Image.new("1", (epd.height, epd.width), 0xFF)  # 0xFF: clear the frame
        draw = ImageDraw.Draw(Himage)

        # ONEOFFTIME takes time from the command line, shows quote once and
        # quits, mainly for testing.
        if options.ONEOFFTIME == None:
            current_time = datetime.now()
            hour = str(current_time.hour).zfill(2)
            minute = str(current_time.minute).zfill(2)
        else:
            hour, minute = options.ONEOFFTIME.split(":")

        logging.debug(f"Processing time {hour}:{minute}")

        texttime, snippet, title, author = read_random_snippet(hour, minute)
        snippet = clean_snippet(snippet)

        linelist = split_and_encode_bold(snippet, texttime, NORMAL_FONT_LINE_WIDTH)
        if len(linelist) <= NORMAL_FONT_MAX_LINES:
            REGULAR_FONT = NORMAL_REGULAR_FONT_20
            BOLD_FONT = NORMAL_BOLD_FONT_20
        else:
            linelist = split_and_encode_bold(snippet, texttime, SMALL_FONT_LINE_WIDTH)
            REGULAR_FONT = SMALL_REGULAR_FONT_16
            BOLD_FONT = SMALL_BOLD_FONT_16

        # Split Title and author if they run off the side of the display
        titleauthortext = "- " + title + " by " + author
        titleauthorlength = draw.textlength(
            titleauthortext, font=NORMAL_REGULAR_FONT_20
        )
        if titleauthorlength > Himage.width:
            linelist.append("- " + title)
            linelist.append(" by " + author)
        else:
            linelist.append("- " + title + " by " + author)

        verticaloffset = 0
        for line in linelist:
            # Do we have to bold anything on this line?
            if line.find(ENCODING_CHARACTER) != -1:
                beforetext, boldtext, aftertext = line.split(ENCODING_CHARACTER)
                beforetextlength = draw.textlength(beforetext, font=REGULAR_FONT)
                boldtextlength = draw.textlength(boldtext, font=BOLD_FONT)
                draw.text((0, verticaloffset), beforetext, font=REGULAR_FONT, fill=0)
                draw.text(
                    (beforetextlength, verticaloffset),
                    boldtext,
                    font=BOLD_FONT,
                    fill=0,
                )
                draw.text(
                    (beforetextlength + boldtextlength, verticaloffset),
                    aftertext,
                    font=REGULAR_FONT,
                    fill=0,
                )
            else:
                draw.text((0, verticaloffset), line, font=REGULAR_FONT, fill=0)

            verticaloffset = verticaloffset + TEXTLINESVERTICALOFFSET

        # Turn it upside down and back to front if necessary, eg to match
        # orientation of Pi
        if options.FLIPSCREEN:
            Himage = Himage.transpose(Image.FLIP_TOP_BOTTOM)
            Himage = Himage.transpose(Image.FLIP_LEFT_RIGHT)

        logging.debug("Displaying image...")
        epd.display_1Gray(epd.getbuffer(Himage))

        # Sleep the ePaper display which also released SPI resources
        epd.sleep()

        if options.ONEOFFTIME != None:
            logging.debug("oneofftime processed, quitting")
            exit(0)

        time.sleep(PAUSE_BETWEEN_QUOTES)
