#!/usr/bin/env python
import os
import base
import numpy as np
def tasks():
    return [
        CheckEPPub(),
        ]
class CheckEPPub(base.Task):
    """
    Checks if all links between mutations and publications established in the
    epdata table are also present in the reports table.
    """
    def __init__(self):
        super(CheckEPPub, self).__init__('check_ep_pub')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()
            
            # Load all epdata mentions
            q = 'select old, idx, new, pub from epdata'
            epdata_mentions = set()
            for old, idx, new, pub in c.execute(q):
                epdata_mentions.add((old, idx, new, pub))

            # Load all reports
            q = 'select old, idx, new, pub from report'
            reports = set()
            for old, idx, new, pub in c.execute(q):
                reports.add((old, idx, new, pub))
                
            # Compare
            diff = epdata_mentions - reports
            if diff:
                print('-'*60)
                print('EPData establishes mutation-publication links not'
                    ' mentioned in report table')
                print('-'*60)
                for old, idx, new, pub in diff:
                    print(old+str(idx)+new + ' : ' + pub)
                import sys
                sys.exit(1)
            print('[ok] EPData links all listed in reports')

if __name__ == '__main__':
    t = base.TaskRunner()
    t.add_tasks(tasks())
    t.run()    
