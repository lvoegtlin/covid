#!/bin/bash

# Update Script for Server: covid.pillo.ch
cd /home/www/covid/src/
export PYTHONPATH=$PYTHONPATH:/home/www/covid
python3 /home/www/covid/src/runner.py
exit 0
