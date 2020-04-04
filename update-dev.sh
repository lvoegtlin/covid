#!/bin/bash

# Update Script for Server: covid.pillo.ch/dev
cd /home/www/covid-dev/src/
export PYTHONPATH=$PYTHONPATH:/home/www/covid-dev
python3 /home/www/covid-dev/src/runner.py
exit 0
