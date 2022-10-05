#!/bin/sh

PATH_SCRIPT='ICUSBProxy.py'
PATH_LOG='/tmp'

BASEDIR=$(dirname $0)
PID=`/usr/bin/pgrep -f ${BASEDIR}/${PATH_SCRIPT}`

# If no argument
if [ -z "$1" ]; then
    if [ -z "$PID" ]; then
        set -- 'start'
    else
        set -- 'stop'
    fi
fi

case "$1" in
    start)
        echo "Starting ICUSBProxy"
        if [ -z "$PID" ]; then
            nohup python3 ${BASEDIR}/${PATH_SCRIPT} > $PATH_LOG/ICUSBProxy.log 2>&1 &
        fi
        ;;
    restart)
        echo "Restarting ICUSBProxy"
        if [ ! -z "$PID" ]; then
            kill -9 "${PID}"
        fi
        nohup python3 ${BASEDIR}/${PATH_SCRIPT} > $PATH_LOG/ICUSBProxy.log 2>&1 &
        ;;
    stop) 
        echo "Stopping ICUSBProxy"
        if [ ! -z "$PID" ]; then
            kill -9 "${PID}"
        fi
        ;;
    esac