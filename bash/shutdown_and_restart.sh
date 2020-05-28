#!/bin/bash

# This script shutsdown the Computer for a certain time period, then reboots and plays music with a crescendo effect.

MAXVOL=60 # max is64
MINVOL=20
INV_VOL_INCEASE_RATE=1
SUSPEND=true
MUSIC_PATH=~/Music

MY_DIR=$(dirname $0)

validate()
{
    if [ $1 = "-h" ]; then
        echo 'usage: '$0' seconds minutes hours'
        exit 0
    fi

    if [[ $EUID -ne 0 ]]; then
        echo "This script must be run as root"
        exit 1
    fi
    if [ -z "$1" ]; then
        echo "First positional argument must specify suspend time"
        exit 1
    fi
}

master_volume()
{
    local vol=$1
    if [ -z "$vol" ]; then
        local R=$(awk -F"[][]" '/dB/ {print $2 }' <(amixer sget 'Master'))
        echo $(sed 's/%//g' <<< $R)
    else
        amixer sset 'Master' $vol unmute >/dev/null
    fi
}

prep_and_shutdown()
{
    WT=`date '+%s' -d "+ $1 seconds"`
    sudo echo 0 > /sys/class/rtc/rtc0/wakealarm
    sudo echo $WT > /sys/class/rtc/rtc0/wakealarm
    echo $(($WT - $(date '+%s')))' seconds to reboot'

    sleep 1
    if $SUSPEND; then
        systemctl suspend
        echo "Suspend initialized"
    fi
    sleep 1
}

play_music()
{
    inital_volume=$(master_volume)
    master_volume 0
    echo $MY_DIR
    echo "$MY_DIR/recursive_music_play $MUSIC_PATH"
    $MY_DIR/recursive_music_play $MUSIC_PATH >/dev/null 2>&1 &
    MPID=$!
    echo $MPID


    echo "Starting master volume crescendo"
    for ((i=$MINVOL; i<=$MAXVOL; i++)); do
        master_volume $i
        read -rsn1 -t $INV_VOL_INCEASE_RATE input
        if [ ! -z $input ]; then
            cleanup_exit
        fi
    done
    echo "Crescendo finished"
    read -n 1
    cleanup_exit
}

cleanup_exit()
{
    if [ -n "$(ps -p $MPID -o pid=)" ]; then
        kill $MPID 
    fi
#    sudo killall mplayer
    sleep 0.5
    master_volume $inital_volume
    exit 0
}

main()
{
    trap cleanup_exit SIGINT
    validate $1
    prep_and_shutdown $1
    play_music
    exit 0
}

main $1
