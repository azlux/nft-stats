#!/usr/bin/env bash

# Exit the script if any of the commands fail
set -e
set -u
set -o pipefail

# Set working directory to the location of this script
cd "$(dirname "${BASH_SOURCE[0]}")"

STARTDIR="$(pwd)"
DESTDIR="$STARTDIR/pkg"
OUTDIR="$STARTDIR/deb"
# get version
repo="azlux/nft-stats"
api=$(curl --silent "https://api.github.com/repos/$repo/releases/latest")
new=$(echo $api | grep -Po '"tag_name": "\K.*?(?=")')

# Remove potential leftovers from a previous build
rm -rf "$DESTDIR" "$OUTDIR"


## nft-stats
install -Dm 755 "$STARTDIR/nft-stats.py" "$DESTDIR/usr/local/bin/nft-stats"

# Build .deb
mkdir "$DESTDIR/DEBIAN" "$OUTDIR"
cp "$STARTDIR/debian/"* "$DESTDIR/DEBIAN/"

# Set version
sed -i "s/VERSION-TO-REPLACE/$new/" "$DESTDIR/DEBIAN/control"

dpkg-deb --build "$DESTDIR" "$OUTDIR"
