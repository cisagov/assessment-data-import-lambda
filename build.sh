#!/usr/bin/env bash

###
# Define the name of the Lambda zip file being produced
###
ZIP_FILE=assessment-data-import.zip

###
# Set up the Python virtual environment
###
VENV_DIR=/venv
python -m venv $VENV_DIR
source $VENV_DIR/bin/activate

###
# Update pip and setuptools
###
pip install --upgrade pip setuptools

###
# Install local assessment data import (adi) module
###
pip install -r requirements.txt

###
# Install other requirements
###
pip install --upgrade docopt>=0.6.2 pymongo>=3.7.2 pytz>=2019.1

###
# Leave the Python virtual environment
###
deactivate

###
# Set up the build directory
###
BUILD_DIR=/build

###
# Copy all packages, including any hidden dotfiles.  Also copy the
# local adi package and the Lambda handler.
###
cp -rT $VENV_DIR/lib/python3.6/site-packages/ $BUILD_DIR
cp -rT $VENV_DIR/lib64/python3.6/site-packages/ $BUILD_DIR
cp -r adi $BUILD_DIR
cp lambda_handler.py $BUILD_DIR

###
# Zip it all up
###
OUTPUT_DIR=/output
if [ ! -d $OUTPUT_DIR ]
then
    mkdir $OUTPUT_DIR
fi

if [ -e $OUTPUT_DIR/$ZIP_FILE ]
then
    rm $OUTPUT_DIR/$ZIP_FILE
fi
cd $BUILD_DIR
zip -rq9 $OUTPUT_DIR/$ZIP_FILE .
