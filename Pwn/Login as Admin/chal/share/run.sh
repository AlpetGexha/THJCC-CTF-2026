#!/bin/sh

exec 2>/dev/null
timeout 60 /home/chal/ld-linux-x86-64.so.2 --library-path /home/chal /home/chal/chal
