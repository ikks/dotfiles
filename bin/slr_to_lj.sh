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

The resulting zip file is a valid contains a subdirectory wavs/
with
 * wav files downsampled to 22050 hz
 * a LICENSE file
 * a transcription for multivoice piper training
 * a piper_voice.txt file for each voice with the transcription
 for single voice piper training
 * a melo_voice.txt file for each voice with the transcription for
 melo training

We require a .zip file downloaded from https://www.openslr.org/
We will create a file.lj.zip file inside this same directory,
we need to be able to write to a temp dir during the process and current
directory.  Download the zip file and run the script where the
zip file was downloaded.  Please do it in a clean directory with
only the downloaded zip file.

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

TMPDIR=`mktemp -d`

echo Unpacking $1
unzip $1 > /dev/null

VOICES=`ls -lf *wav | grep wav | gawk '{print $9}' | gawk -F_ '{print $1"_"$2}' | sort -u | head`

echo A total of `ls -l *wav | wc -l` wav files with `echo $VOICES | wc -w` voices

mkdir -p wavs

# lsj file Transcription
sed -E 's/([a-z]+_[0-9]+)(_[0-9]+)\t(.*)$/wavs\/\1\2.wav|\1|\3/' line_index.tsv > wavs/_transcription.txt

for i in $VOICES; do
    grep $i wavs/_transcription.txt | gawk -F'|' '{print $1"|"$3}' > wavs/piper_"$i".txt
    grep $i wavs/_transcription.txt  > wavs/melo_"$i".txt
done
exit 0
mv LICENSE wavs

# We use fd because we want to be able to parallelize the downsampling
echo Down sampling to 22050 Hz
fd -e wav -x sox '{}' -r 22050 $TMPDIR/'{/}'

echo cleaning
rm *wav *tsv
mv $TMPDIR/*wav wavs
rm -rf $TMPDIR

NEW_ZIP="${1%.zip}".lj.zip
echo compressing $NEW_ZIP

zip -r $NEW_ZIP wavs > /dev/null
rm -rf wavs
