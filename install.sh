#!/bin/bash
# NetCrash V1.0 - installer
# Installs the `netcrash` command so you can run it like nmap:
#   netcrash example.com
#
# Usage:
#   chmod +x install.sh
#   ./install.sh

set -e
cd "$(dirname "$0")"

if [ ! -f "netcrash.py" ]; then
    echo "Error: netcrash.py not found in this folder."
    exit 1
fi

chmod +x netcrash.py

if [ -w /usr/local/bin ]; then
    cp netcrash.py /usr/local/bin/netcrash
else
    echo "Need sudo to install to /usr/local/bin."
    sudo cp netcrash.py /usr/local/bin/netcrash
fi

chmod +x /usr/local/bin/netcrash

echo "NetCrash V1.0 installed."
echo "Try it: netcrash example.com"
echo "Help:   netcrash --help"
