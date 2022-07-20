"""
command for checking databases ready
"""
import time
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """ Django command to wait for dateBase """
    def handle(self, *args, **options):
        """ Entry point for command"""
        self.stdout.write('wait for dateBase ...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases= ["default"])
                db_up = True
            except(Psycopg2Error,OperationalError):
                self.stdout.write('dataBase is not available , waiting for 1 second...')
                time.sleep(1)
         
        self.stdout.write(self.style.SUCCESS('dateBase is available'))      
        