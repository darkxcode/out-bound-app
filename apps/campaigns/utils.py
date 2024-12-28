import datetime
import email
import email.utils
import imaplib
import logging
import poplib
import re
import smtplib
import sys
from email import message_from_bytes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pytz
from django.conf import settings
from django.db.models import Q
from django.utils.html import strip_tags
from flufl.bounce import scan_message

from .models import Campaign, Recipient, Mailbox, Message

# Enable logging
logging.basicConfig(stream=sys.stdout, level='DEBUG')


def get_replied_addresses(mailbox_obj: Mailbox) -> set:
    """
    :param mailbox_obj: :type Mailbox object.
    :return: List of all contacts which were in ['From'] header in mailbox. :type list
    """

    try:
        logging.info('[+] Exporting contacts who replied.')
        contacts = list()
        email_pattern = r'[\w\.\+\-]+\@[\w\.\+\-]+\.[a-z]{2,3}'
        mailbox = imaplib.IMAP4_SSL(mailbox_obj.host)
        mailbox.login(mailbox_obj.host_user, mailbox_obj.host_password)
        mailbox.select()
        typ, data = mailbox.search(None, 'ALL')
        for num in data[0].split():
            typ, data = mailbox.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])
            contacts.append(re.findall(email_pattern, msg['From'])[0])
        mailbox.close()
        mailbox.logout()
        logging.debug(f'[+] Contacts who replied are: {contacts}.')
        logging.info('[+] Exporting contacts who replied was finished.')
        return set(contacts)

    except imaplib.IMAP4.error as error:
        logging.debug(f'[-] There was an error {error} in {mailbox_obj.host_user} config.')


def create_and_send_email(sender=None, sender_name=None, recipient=None,
                          body_html=None, username_smtp=None, password_smtp=None,
                          host_smtp='email-smtp.us-east-1.amazonaws.com', port_smtp=587, subject=None) -> bool:
    """
    Function sends emails to 'Contact' objects.
    :param sender: For example: 'myemail@gmail.com' :type str
    :param sender_name: For example: 'Alexandr S.' :type str
    :param recipient: For example: 'myemail@gmail.com' :type str
    :param body_html: :type str
    :param username_smtp: Amazon SES account SMTP username :type str
    :param password_smtp: Amazon SES account SMTP password :type str
    :param host_smtp: For example: 'email-smtp.us-east-1.amazonaws.com' :type str
    :param port_smtp: For example: 587 :type int
    :param subject: Subject for message :type str
    :return :type bool
    """

    logging.debug(f'[+] START create_and_send_email()')
    logging.debug(f'[+] Creating message: ')
    logging.debug(f'[+] sender: {sender}.')
    logging.debug(f'[+] sender_name: {sender_name}.')
    logging.debug(f'[+] recipient: {recipient}.')
    logging.debug(f'[+] subject: {subject}.')
    logging.debug(f'[+] body_html: {body_html}.')
    logging.debug(f'[+] host_smtp: {host_smtp}.')
    logging.debug(f'[+] port_smtp: {port_smtp}.')

    try:
        # Add tracker
        body_html += f'<br><img width="1px" height="1px" src="https://www.myschedule.pro/contact/{recipient}/open_message/"/>'
        # Continue process
        body_plain_text = strip_tags(body_html)

        message = email.mime.multipart.MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = email.utils.formataddr((sender_name, sender))
        message['To'] = recipient

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = email.mime.text.MIMEText(body_plain_text, 'plain')
        part2 = email.mime.text.MIMEText(body_html, 'html')
        message.attach(part1)
        message.attach(part2)

        logging.debug('[+] Creating message was finished.')
        logging.debug('[+] Trying to send new message.')
        server = smtplib.SMTP(host_smtp, port_smtp)
        server.ehlo()
        server.starttls()
        # smtplib docs recommend calling ehlo() before & after starttls()
        server.ehlo()
        server.login(username_smtp, password_smtp)
        server.sendmail(sender, recipient, message.as_string())
        server.close()
        logging.debug('[+] New message was successfully sent.')
        logging.debug(f'[+] FINISH create_and_send_email().')
        return True

    except Exception as error:
        logging.debug(f'[-] ERROR There was an error {error}.')
        return False


def replace_tags(subject: str, message: str, contact: Recipient):
    logging.debug(f'[+] START replace_tags()')
    logging.debug(f'[+] Replacing tags in subject and message.')
    t = ((r'\{\{.*?First Name.*?\}\}', contact.first_name),
         (r'\{\{.*?Last Name.*?\}\}', contact.last_name),
         (r'\{\{.*?Company Name.*?\}\}', contact.company_name),
         (r'\{\{.*?Snippet 1.*?\}\}', contact.snippet_1),
         (r'\{\{.*?Snippet 2.*?\}\}', contact.snippet_2),
         (r'\{\{.*?Snippet 3.*?\}\}', contact.snippet_3))

    for pattern, string in t:
        subject = re.sub(pattern, string, subject)
        message = re.sub(pattern, string, message)
    logging.debug(f'[+] Replacing tags in subject and message was finished.')
    logging.debug(f'[+] FINISH replace_tags().')
    return message, subject


def get_bounced_addresses(pop_server: str, port: int, email_address: str, password: str) -> set:
    logging.info('[+] START get_bounced_addresses()')
    logging.info('[+] Exporting bounced email addresses.')
    # breaks with if this is left out for some reason (MAXLINE is set too low by default.)
    poplib._MAXLINE = 20480
    pop_conn = poplib.POP3_SSL(pop_server, port)
    pop_conn.user(email_address)
    pop_conn.pass_(password)

    # Get messages from server:
    messages = [pop_conn.retr(i) for i in range(1, len(pop_conn.list()[1]) + 1)]
    # Concat message pieces:
    messages = [b"\n".join(msg[1]) for msg in messages]

    bounced_emails = []
    bounced_emails_raw = []

    # TODO: refactor list in list processing
    for msg in messages:
        bounced_emails_raw.append(scan_message(message_from_bytes(msg)))

    bounced_emails_raw = [i for i in bounced_emails_raw if len(i) >= 1]

    for emails_set in bounced_emails_raw:
        for e in emails_set:
            bounced_emails.append(str(e, 'utf-8'))

    logging.debug(f'[+] Bounced emails are: {bounced_emails}.')
    logging.info('[+] Exporting bounced email addresses was finished.')
    logging.info('[+] FINISH get_bounced_addresses()')
    return set(bounced_emails)


def update_flags_for_campaign_recipients(campaign: Campaign):
    # Bounced
    bounced_addresses = get_bounced_addresses("pop.gmail.com", 995, campaign.mailbox.host_user,
                                              campaign.mailbox.host_password)
    # Replied
    replied_addresses = get_replied_addresses(campaign.mailbox)

    # Mark contacts who replied as replied in db
    campaign.recipients.filter(email__in=replied_addresses).update(opened_message=True, replied=True)

    # Mark bounced addresses as bounced in db
    Recipient.objects.filter(email__in=bounced_addresses).update(bounced=True)


def run_campaign(campaign: Campaign):
    """
    If campaign was finished:
    -restore 'processed' state to False
    -increment 'current_message_index'.
    ************************************
    If no recipients for campaign:
    -increment 'current_message_index'.
    -deactivate campaign if no more messages available
    """

    update_flags_for_campaign_recipients(campaign)

    # If no recipients for processing
    if not campaign.recipients.exclude(Q(processed=True) | Q(replied=True) | Q(bounced=True)).exists():
        # Get and update current relevant (or default) message for campaign.
        message = campaign.get_current_campaign_message()
        message.opened = campaign.recipients.filter(opened_message=True).count()
        message.replied = campaign.recipients.filter(replied=True).count()
        message.total_sent = campaign.total_messages_counter
        message.save(update_fields=['opened', 'replied', 'total_sent'])

        campaign.current_message_index += 1
        campaign.save(update_fields=['current_message_index'])

        campaign.deactivate_recipients()

        if campaign.current_message_index >= campaign.messages.count():
            campaign.deactivate_campaign()

    if campaign.is_active:
        message = campaign.get_current_campaign_message()

        # Send message for every non-processed contact.
        recipients_to_process = campaign.recipients.filter(replied=False, processed=False, bounced=False)
        r_count = recipients_to_process.count()
        limit = r_count if r_count < campaign.daily_limit else campaign.daily_limit

        time_now = pytz.timezone("America/New_York").localize(datetime.datetime.now())

        counter = 1
        for recipient in recipients_to_process:

            # Add time for new recipients object.
            if recipient.next_processed_time is None:
                delta = datetime.timedelta(days=campaign.interval)
                recipient.next_processed_time = time_now - delta
                recipient.save(update_fields=['next_processed_time'])

            # Check recipients next_processed_time status.
            elif recipient.next_processed_time <= time_now:
                if counter <= limit:
                    msg, subj = replace_tags(message.subject, message.text, recipient)

                    result = create_and_send_email(
                        sender=campaign.mailbox.host_user,
                        sender_name=campaign.mailbox.full_name,
                        recipient=recipient.email,
                        body_html=msg,
                        subject=subj,
                        port_smtp=settings.AMAZON_SES_ACCOUNT['port'],
                        host_smtp=settings.AMAZON_SES_ACCOUNT['host'],
                        username_smtp=settings.AMAZON_SES_ACCOUNT['username'],
                        password_smtp=settings.AMAZON_SES_ACCOUNT['password'],
                    )
                    if result:
                        recipient.processed = True
                        time = time_now + datetime.timedelta(days=campaign.interval)
                        recipient.next_processed_time = time
                        recipient.save(update_fields=['processed', 'next_processed_time'])
                        counter += 1
                        campaign.total_messages_counter += 1
                        campaign.save(update_fields=['total_messages_counter'])


def get_campaigns(time_now: str, day_of_the_week: str):
    time_tuples = [str((i, 0)) for i in range(24)]
    if time_now in time_tuples:
        campaign_parameters = {f'is_active_on_{day_of_the_week.lower()}': True,
                               f'{day_of_the_week.lower()}_start_time': time_now}
        return Campaign.objects.filter(is_active=True, **campaign_parameters)
    return Campaign.objects.none()
