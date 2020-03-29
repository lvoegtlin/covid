#!/bin/bash
# run daily to update covid stats

python creating_report.py

msg="automatic_update"$(date "+%D")

git add *
git commit -m ${msg}
git push
