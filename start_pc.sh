#!/usr/bin/bash
# Get color codes from strformat.py. This cstr is simply designed for foreground colors.
RED=31
GREEN=32

function cstr () {
    if [ "$2" ]
    then
        echo -e "\033[$2m$1\033[0m"
    fi
}

function check_integrity() {
    for fname in "$@"
    do
      result=$(find . -name "$fname")
      if [ ! "$result" ]
      then
        cstr "$fname not in current working directory. Change to PixCrawl folder instead." $RED
        exit 1
      fi
    done
}

check_integrity "args.json" "check_browser.py" "cli.py" "crawler.py" "database.py" \
"doujin.py" "downloader.py" "native_crawler.py" "pixcrawl.py" "pixiv_crawler.py" \
"preinit.py" "startups.json" "strformat.py"

cstr "File integrity check passed." $GREEN

if [ ! "$(command -v python3.10)" ]
then
    cstr "Python version 3.10 does not exist on your computer." $RED
    exit 1
fi


check=1
for arg in "$@"
do
    if [ "$arg" = "--nocheck" ]
    then
        check=0
        break
    fi
done

if [ $check = 1 ]
then
    echo -n "Run pre-initialization and check browser status? [Y/n]: "
    read -r conf
    if [ "$conf" = 'Y' ] || [ "$conf" = 'y' ] || [ "$conf" = '' ]
    then
        python3.10 preinit.py
    fi
fi

if [ ! -f "./venv/bin/activate" ]; then
    cstr "Virutual environment not detected. Try run with pre-initialization first." $RED
    exit 1
fi

source ./venv/bin/activate
cstr "Program has been successfully started." $GREEN
python pixcrawl.py "$@"