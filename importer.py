#!/usr/bin/env python3
from tinydb import TinyDB, Query
import logging
logging.basicConfig(level=logging.DEBUG)
DATAFILE='/media/Dmitrijs_Covid_sorting/tabula.csv'
db=TinyDB('/opt/dmitri/data.json')
db.truncate()
print(db.all())
q=Query()
duplicates=0
errors=0
with open(DATAFILE) as f:
    for l in f:
        try:
            l=l.strip()
            if len(db.search(q.sample == l)) == 0:
                db.insert({'sample':l})
                logging.info('Adding {}'.format(l))
            else:
                duplicates += 1
        except ValueError as e:
            errors += 1
logging.info('{} files added, {} duplicates, {} errors'.format(len(db),duplicates,errors))
