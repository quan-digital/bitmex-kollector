#!/usr/bin/env bash
while true;
do
PID=`cat kollector.pid`

if ! ps -p $PID > /dev/null
then
  rm pyno.pid
  python3 util/mail.py
  python3 main.py & echo $! >>kollector.pid
fi
sleep 3; 
done