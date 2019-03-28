#!/bin/bash

printhelp()
{
  echo "Usage: backup backupDriveRootDirectory"
}

if [ "$#" -eq 0 ]
then
  printhelp
  exit 1
fi

date=$(date -Is)
createdNewDir=""

backupDirectoryRoot=$1
backupDirNoWild=$backupDirectoryRoot/home_and_data_backup
backupDir=$backupDirNoWild*
newBackupDir=$backupDirNoWild"_"$date

echo "> Targeted backup dir is $newBackupDir"
if [ ! -d $backupDir ]; then
  echo "> $backupDirNoWild does not exist, creating"
  mkdir $newBackupDir || exit 0
  createdNewDir=1
fi

dirs=( $backupDir )
if [ ! -z ${dirs[1]} ]; then
  echo "> there are multiple backup directories in the drive, only one is allowed"
  echo "  at least 2 directories exist ${dirs[0]} and ${dirs[1]}"
  exit 1
fi
echo "> In $backupDirectoryRoot found $backupDir as backupdir to use"

if [ -z $createdNewDir ]; then
  echo "> renaming $backupDir to $newBackupDir"
  mv $backupDir $newBackupDir
fi

printf "> starting transfer \n\n"

rsync --archive --human-readable --delete --info=progress2 ~ $backupDir
