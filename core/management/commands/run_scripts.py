from django.core.management.base import BaseCommand, CommandError
from core.my_custom_functions import update_balances,update_due_balances,do_next_create_links_if_ready, do_next_settle_mkts_if_ready, do_next_create_challenge_links_if_ready, do_next_settle_challenge_mkts_if_ready
import threading
import time

def always_update_balances():
    while True:
        time.sleep(10)
        update_balances()

def always_update_due_balances():
    while True:
        time.sleep(10)
        update_due_balances()

def always_do_next_create_links_if_ready():
    while True:
        time.sleep(10)
        do_next_create_links_if_ready()

def always_do_next_create_challenge_links_if_ready():
    while True:
        time.sleep(10)
        do_next_create_challenge_links_if_ready()

def always_do_next_settle_mkts_if_ready():
    while True:
        time.sleep(10)
        do_next_settle_mkts_if_ready()

def always_do_next_settle_challenge_mkts_if_ready():
    while True:
        time.sleep(10)
        do_next_settle_challenge_mkts_if_ready()


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass
    def handle(self, *args, **options):
        thread1 = threading.Thread(target=always_update_balances)
        thread2 = threading.Thread(target=always_update_due_balances)
        thread3 = threading.Thread(target=always_do_next_create_links_if_ready)
        thread4 = threading.Thread(target=always_do_next_create_challenge_links_if_ready)
        thread5 = threading.Thread(target=always_do_next_settle_mkts_if_ready)
        thread6 = threading.Thread(target=always_do_next_settle_challenge_mkts_if_ready)

        thread1.start()
        thread2.start()
        thread3.start()
        thread4.start()
        thread5.start()
        thread6.start()

        thread1.join()
        thread2.join()
        thread3.join()
        thread4.join()
        thread5.join()
        thread6.join()
       


