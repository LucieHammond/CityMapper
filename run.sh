#!/bin/sh

# Add root directory to pythonpath
export PYTHONPATH=$PYTHONPATH:`pwd`

# Run GUI from starting point
python2.7 gui/home.py