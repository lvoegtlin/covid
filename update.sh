#!/bin/bash

# Update Script for Server: covid.pillo.ch
cd /home/www/covid/
export PYTHONPATH=$PYTHONPATH:/home/www/covid
python3 /home/www/covid/src/runner.py
exit 0
