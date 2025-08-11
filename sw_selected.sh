#!/bin/bash
export YDOTOOL_SOCKET=/tmp/.ydotool_socket
sudo chmod go+rwx /tmp/.ydotool_socket
_python=/home/buba/Projects/lipunto/.venv/bin/python
"${_python}" /usr/local/sbin/switch_layout.py selected
