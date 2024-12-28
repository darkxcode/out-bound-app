from django.test import TestCase
from mixer.backend.django import mixer

from .models import *
from .utils import *


class MailerTests(TestCase):
    def setUp(self):
        # use real test gmail account
        self.test_email = 'cotcet123@gmail.com'
        self.test_email_passwd = ')9)mVf-zJzHJFjCR'

        # use real gmail recipients email
        real_recipients = ['vvkhromoff@gmail.com',  # !!! replied
                           'johnzorn1988@gmail.com',
                           '9203377@gmail.com',
                           'alexandr@raisesoftware.com',
                           'cloth.boutique@tuta.io',
                           'dokdak322@gmail.com']
        real_recipients_gen = (e for e in real_recipients)
        messages_gen = (f'Message No {n}' for n in range(1, 6))

        self.test_time = pytz.timezone("America/New_York").localize(datetime.datetime.now()) - datetime.timedelta(days=1)

        self.user = mixer.blend(User)
        self.mailbox = mixer.blend(Mailbox, owner=self.user, host_user=self.test_email,
                                   host_password=self.test_email_passwd)
        self.campaign = mixer.blend(Campaign, creator=self.user, mailbox=self.mailbox,
                                    current_message_index=0, daily_limit=2)

        self.recipients_bounced = mixer.cycle(5).blend(Recipient, campaign=self.campaign,
                                                       # spreadsheet=None,
                                                       bounced=True, next_processed_time=self.test_time)
        self.recipients_replied = mixer.cycle(5).blend(Recipient, campaign=self.campaign,
                                                       # spreadsheet=None,
                                                       replied=True, next_processed_time=self.test_time)
        # TODO:try with not verified fake addresses
        # self.fake_recipients_not_processed = mixer.cycle(5).blend(Recipient, campaign=self.campaign,
        #                                                            spreadsheet=None,
                                                                   # processed=False,
                                                                  # next_processed_time=self.test_time)
        self.real_recipients_not_processed = mixer.cycle(len(real_recipients)).blend(
            Recipient, campaign=self.campaign, email=real_recipients_gen,
            # spreadsheet=None,
            processed=False, next_processed_time=self.test_time
        )

        self.messages = mixer.cycle(5).blend(
            Message, campaign=self.campaign, subject=messages_gen,
            # spreadsheet=None,
            processed=False, next_processed_time=self.test_time
        )

    def run_campaign_with_refresh(self, campaign):
        run_campaign(campaign)
        [i.refresh_from_db() for i in self.real_recipients_not_processed]
        [i.refresh_from_db() for i in self.messages]
        campaign.refresh_from_db()

    def test_run_campaign_when_current_message_index_0(self):
        campaign = self.campaign
        replied_recipient = [r for r in self.real_recipients_not_processed if r.email == 'vvkhromoff@gmail.com'][0]

        # region Cicle 1 with daily_limit = 2, message No 1
        self.run_campaign_with_refresh(campaign)

        # check message id = 1
        message = campaign.get_current_campaign_message()
        self.assertEqual(message.id, 1)
        self.assertEqual(message.replied, 0)

        # -> 'vvkhromoff@gmail.com: replied=True, opened=True,
        # -> 2 real_recipients processed
        self.assertTrue(replied_recipient.replied, True)
        self.assertTrue(replied_recipient.opened_message, True)
        self.assertEqual([i.processed for i in self.real_recipients_not_processed].count(True), 2)
        self.assertEqual([i.replied for i in self.real_recipients_not_processed].count(True), 1)
        self.assertEqual([i.opened_message for i in self.real_recipients_not_processed].count(True), 1)
        self.assertEqual(campaign.recipients.filter(processed=True).count(), 2)

        #  4 Real (6 orgilinal list - 2)
        #  5 Fake recipients_bounced
        #  5 Fake recipients_replied + 1 Real
        #  TODO: 5 Fake recipients not processed: 5
        self.assertEqual(campaign.recipients.filter(processed=False).count(), 14)
        self.assertEqual(campaign.recipients.filter(bounced=True).count(), 5)
        self.assertEqual(campaign.recipients.filter(replied=True).count(), 6)
        # endregion

        # region Cicle 2 with daily_limit = 2, message No 1
        self.run_campaign_with_refresh(campaign)

        # check message id = 1
        message = campaign.get_current_campaign_message()
        self.assertEqual(message.id, 1)
        self.assertEqual(message.replied, 0)

        # -> 'vvkhromoff@gmail.com: replied=True, opened=True,
        # -> 2 + 2 real_recipients processed
        self.assertTrue(replied_recipient.replied, True)
        self.assertTrue(replied_recipient.opened_message, True)
        self.assertEqual([i.processed for i in self.real_recipients_not_processed].count(True), 4)
        self.assertEqual([i.replied for i in self.real_recipients_not_processed].count(True), 1)
        self.assertEqual([i.opened_message for i in self.real_recipients_not_processed].count(True), 1)
        self.assertEqual(campaign.recipients.filter(processed=True).count(), 4)

        #  2 Real (6 orgilinal list - 4)
        #  5 Fake recipients_bounced
        #  5 Fake recipients_replied + 1 Real
        #  TODO: 5 Fake recipients not processed: 5
        self.assertEqual(campaign.recipients.filter(processed=False).count(), 12)
        self.assertEqual(campaign.recipients.filter(bounced=True).count(), 5)
        self.assertEqual(campaign.recipients.filter(replied=True).count(), 6)
        # endregion

        # region Cicle 3 with daily_limit = 2, message No 1
        self.run_campaign_with_refresh(campaign)

        # check message id = 1
        message = campaign.get_current_campaign_message()
        self.assertEqual(message.id, 1)
        self.assertEqual(message.replied, 0)

        # -> 'vvkhromoff@gmail.com: replied=True, opened=True,
        # -> 2 + 2 + 1 real_recipients processed
        # -> 1 fake_recipients processed
        self.assertTrue(replied_recipient.replied, True)
        self.assertTrue(replied_recipient.opened_message, True)
        self.assertEqual([i.processed for i in self.real_recipients_not_processed].count(True), 5)
        self.assertEqual([i.replied for i in self.real_recipients_not_processed].count(True), 1)
        self.assertEqual([i.opened_message for i in self.real_recipients_not_processed].count(True), 1)
        # self.assertEqual(campaign.recipients.filter(processed=True).count(), 6)

        #  0 Real
        #  5 Fake recipients_bounced
        #  5 Fake recipients_replied + 1 Real
        #  TODO: 5 Fake recipients not processed (): 5
        self.assertEqual(campaign.recipients.filter(processed=False).count(), 11)
        self.assertEqual(campaign.recipients.filter(bounced=True).count(), 5)
        self.assertEqual(campaign.recipients.filter(replied=True).count(), 6)
        # endregion

        # region Circle 4 with daily_limit = 2, message No 2
        # all tests should be like Circle 1

        # monkey punch to start new circle
        # cos dates were changed to greater than nowdate
        for r in campaign.recipients.all():
            r.next_processed_time=self.test_time
            r.save(update_fields=['next_processed_time'])

        self.run_campaign_with_refresh(campaign)

        # check message id = 2
        message = campaign.get_current_campaign_message()
        old_message = Message.objects.get(id=message.id-1)

        # check old message fields
        self.assertEqual(old_message.opened, 1)
        self.assertEqual(old_message.replied, 6)
        self.assertEqual(old_message.total_sent, 5)

        self.assertEqual(message.id, 2)
        self.assertEqual(message.replied, 0)

        # -> 'vvkhromoff@gmail.com: replied=True, opened=True,
        # -> 2 real_recipients processed
        self.assertTrue(replied_recipient.replied, True)
        self.assertTrue(replied_recipient.opened_message, True)
        self.assertEqual([i.processed for i in self.real_recipients_not_processed].count(True), 2)
        self.assertEqual([i.replied for i in self.real_recipients_not_processed].count(True), 1)
        self.assertEqual([i.opened_message for i in self.real_recipients_not_processed].count(True), 1)
        self.assertEqual(campaign.recipients.filter(processed=True).count(), 2)

        #  4 Real (6 orgilinal list - 2)
        #  5 Fake recipients_bounced
        #  5 Fake recipients_replied + 1 Real
        #  TODO: 5 Fake recipients not processed: 5
        self.assertEqual(campaign.recipients.filter(processed=False).count(), 14)
        self.assertEqual(campaign.recipients.filter(bounced=True).count(), 5)
        self.assertEqual(campaign.recipients.filter(replied=True).count(), 6)
        # endregion
