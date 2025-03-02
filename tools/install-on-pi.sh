#!/usr/bin/env bash
# ------------------------------------------------------------------------------
#
# File          - install-on-pi.sh
#
# Description   - Install literature-clock-epaper.py on Pi
#
# Find me       - https://github.com/alexdyas/literature-clock-epaper/blob/main/tools/install-on-pi.sh
#
# Usage         - ./install-on-pi.sh -d <destination path> -i <remote server address> -u <remote user>
#
# ------------------------------------------------------------------------------

# - Bail on problems -----------------------------------------------------------
set -e

usage() {
  echo "Usage: $0 [-d <destination path>] [-i <remote server address>] [-u <remote user>]" 1>&2
  echo "Run from git repo root directory"
  exit 1
}

while getopts ":d:i:u:" o; do
    case "${o}" in
        d)
            DESTINATIONPATH=${OPTARG}
            ;;
        i)
            REMOTEIP=${OPTARG}
            ;;
        u)
            REMOTEUSER=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${DESTINATIONPATH}" ] || [ -z "${REMOTEIP}" ] || [ -z "${REMOTEUSER}" ]; then
    usage
fi


echo Installing to ${REMOTEIP} at ${DESTINATIONPATH} on behalf of ${REMOTEUSER}

# - Main event -----------------------------------------------------------------
rsync --archive                           \
      --verbose                           \
      --compress                          \
      --progress                          \
      --delete-after                      \
      --exclude '.DS_Store'               \
      --exclude '.DS_Store'               \
      --exclude '.Trashes*'               \
      --exclude '.HFS+'                   \
      --exclude '.TemporaryItems'         \
      --exclude '.bzvol*'                 \
      --exclude '.Spotlight*'             \
      --exclude '.fseventsd*'             \
      --exclude '.DocumentRevisions-V100' \
      --exclude '*.swp'                   \
      --exclude '__pycache__'             \
      src/ ${REMOTEUSER}@${REMOTEIP}:${DESTINATIONPATH}/

rsync --archive                           \
      --verbose                           \
      --compress                          \
      --progress                          \
      --delete-after                      \
      --exclude '.DS_Store'               \
      --exclude '.Trashes*'               \
      --exclude '.HFS+'                   \
      --exclude '.TemporaryItems'         \
      --exclude '.bzvol*'                 \
      --exclude '.Spotlight*'             \
      --exclude '.fseventsd*'             \
      --exclude '.DocumentRevisions-V100' \
      --exclude '*.swp'                   \
      data/ ${REMOTEUSER}@${REMOTEIP}:${DESTINATIONPATH}/data
