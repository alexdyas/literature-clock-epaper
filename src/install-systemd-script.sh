#!/usr/bin/env bash
# ------------------------------------------------------------------------------
#
# File          - install-systemd-script.sh
#
# Description   - Install and enable systemd script for literature-clock-epaper
#
# Find me       - https://github.com/alexdyas/literature-clock-epaper/blob/main/src/install-systemd-script.sh
#
# Usage         - Without command line parameters - install and enable systemd
#                 service for literature-clock-epaper
#               - Run with disable as param, disable the service
#
# Notes         - Requires sudo privaledges
# ------------------------------------------------------------------------------

set -e

if [ "$1" = "disable" ]
then
  echo Disabling literature-clock-epaper service
  sudo systemctl disable --now literature-clock-epaper.service
  exit 0
fi

echo Installing and enabling literature-clock-epaper service
sudo cp literature-clock-epaper.service /etc/systemd/system/
sudo systemctl enable --now literature-clock-epaper.service
sudo systemctl start literature-clock-epaper.service
