#!/bin/bash
# This script is given to Public Domain with no warranties
#
# This script eases the process of adding voices to piper project.
# Making it easier to i18n and l10n thanks to Google work on 2019
# to regionalize voices and open with a permisive license
# (Attribution-ShareAlike 4.0 International)
#
# Take a look at https://www.openslr.org/72/ for further deatils
# on the structure of the .zip file, that needs to contain a
# LICENSE, a transcription line_index.tsv and the wav files
#
# Author: Igor Támara<igor.tamara@gmail.com>

usage () {
cat << EOF

usage: $0 file.zip

This script creates a zip file with appropiate structure to train
piper voices from an origin file from the openslr project.

Many wavs and a tsv with two columns, the first is the name of the
wav file and the second is the transcription.

The original files are downsampled to 22050 Hz.

The resulting zip file contains:
 * a LICENSE file
 * a metadata.csv two column file
 * a _transcription.txt for multivoice piper training three column
 file
 * a piper_voice.txt two column file for each voice with the 
 transcription.
 * a subdirectory wavs/ with wav files downsampled to 22050 hz

We require a .zip file downloaded from https://www.openslr.org/
We will create a file.lj.zip file inside this same directory.
Download the zip file and run the script where the zip file was
downloaded.  Please do it in a clean directory with only the
downloaded zip file.

We will need you to have installed unzip, zip, gawk, fd and sox

In Debian you can issue
 sudo apt install unzip gawk fd-find sox
to install the required packages.

EOF
}
if [[ ! $# -eq 1 ]]; then
  usage
  exit 1
fi

if [ ! -f $1 ]; then
  usage
  exit 1
fi

set -e

TMPDIR=`mktemp -d`

echo Unpacking $1
unzip $1 > /dev/null

VOICES=`ls -lf *wav | gawk -F_ '{print $1"_"$2}' | sort -u`

echo Processing a total of `ls -l *wav | wc -l` wav files with `echo $VOICES | wc -w` voices

mkdir -p wavs

# lsj file Transcription
sed -E 's/([a-z]+_[0-9]+)(_[0-9]+)\t(.*)$/wavs\/\1\2.wav|\1|\3/' line_index.tsv > _transcription.txt
sed -E 's/([a-z]+_[0-9]+)(_[0-9]+)\t(.*)$/wavs\/\1\2.wav|\3/' line_index.tsv > metadata.csv

for i in $VOICES; do
    grep $i _transcription.txt | gawk -F'|' '{print $1"|"$3}' > piper_"$i".txt
done

# We use fd because we want to be able to parallelize the downsampling
echo Down sampling to 22050 Hz
fd -e wav -x sox '{}' -r 22050 wavs/'{/}'

echo cleaning
rm *wav *tsv

NEW_ZIP="${1%.zip}".lj.zip
echo compressing $NEW_ZIP

zip -r $NEW_ZIP wavs LICENSE *.csv *.txt > /dev/null
rm -rf wavs LICENSE *txt *csv > /dev/null
