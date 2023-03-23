import os
import django
from myweb.models import Company
import csv
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")


django.setup()
with open('/myweb/static/stock_company.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        company = Company(
            ts_code=row['ts_code'],
            exchange=row['exchange'],
            reg_capital=float(row['reg_capital']),
            setup_date=row['setup_date'],
            province=row['province'],
            city=row['city'],
            introduction=row['introduction'],
            website=row['website'],
            business_scope=row['business_scope'],
            employees=int(row['employees']),
            main_business=row['main_business']
        )
        company.save()
