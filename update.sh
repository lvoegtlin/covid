#!/bin/bash
# run daily to update covid stats

cd /home/www/covid/
python3 /home/www/covid/creating_report.py
exit 0

msg="automatic_update"$(date "+%D")

git add *
git commit -m ${msg}
git push
