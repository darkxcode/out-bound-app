import calendar
import datetime
import logging
import sys

import pytz

from mailer.celery import app
from .utils import get_campaigns, run_campaign

# Enable logging
logging.basicConfig(stream=sys.stdout, level='DEBUG')


@app.task
def mailer():
    logging.info('[+] START mailer()')
    logging.info('[+] Mailer has been started.')

    day_of_the_week = calendar.day_name[datetime.datetime.now(pytz.timezone('America/New_York')).weekday()]
    new_york_time = datetime.datetime.now(tz=pytz.timezone('America/New_York'))
    time_now = str((new_york_time.hour, new_york_time.minute))

    campaigns = get_campaigns(time_now, day_of_the_week)
    logging.info('[+] Relevant campaigns were collected.')
    logging.debug(f'[+] Campaigns are: {campaigns}.')
    if campaigns.exists():
        for campaign in campaigns:
            logging.info(f'[+] run_campaign() for campaign pk: {campaign.pk}.')
            run_campaign(campaign)
            logging.info(f'[+] run_campaign() for campaign pk: {campaign.pk} finished.')
    logging.info('[+] FINISH mailer()')
