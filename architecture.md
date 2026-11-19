# Architecture

```
 INPUT                      PROCESSING                              OUTPUT
 -----                      ----------                              ------
 data/contacts.csv  ---->  contacts.py   (read + validate)
 data/reminders.csv ---->  scheduler.py  (which are due? repeat?)
 templates/*.txt    ---->  templates_loader.py (personalize)  ---->  outputs/email_report.csv
                           mailer.py     (SMTP or DRY RUN)         logs/app.log
                           reports.py    (CSV + summary)           outputs/state.json (live only)
```
