#!/usr/bin/env bash
while true;
do
PID=`cat kollector.pid`

if ! ps -p $PID > /dev/null
then
  rm kollector.pid
  python3 bitmex_kollector/util/mail.py
  python3 main.py & echo $! >>kollector.pid
fi
sleep 3; 
done
