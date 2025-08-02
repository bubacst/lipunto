#!/bin/bash
export YDOTOOL_SOCKET=/tmp/.ydotool_socket
chmod go+rwx /tmp/.ydotool_socket
/usr/local/sbin/switch_layout.py selected
