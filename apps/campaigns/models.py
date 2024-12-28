import datetime

from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.db import models

from .help_texts import message_subject_help_text, message_text_help_text


class Campaign(models.Model):
    TIME_CHOICES = [
        (str((i, 0)), datetime.time(i).strftime('%I %p')) for i in range(24)
    ]

    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User, related_name='campaigns', on_delete=models.DO_NOTHING)

    # Mailbox
    mailbox = models.ForeignKey('Mailbox', related_name='campaigns', on_delete=models.DO_NOTHING)

    # Service variables
    total_messages_counter = models.PositiveSmallIntegerField(default=0)
    current_message_index = models.PositiveSmallIntegerField(default=0)

    # Custom limitations
    daily_limit = models.PositiveSmallIntegerField(default=100, help_text='Daily limit of outbound messages.')
    interval = models.PositiveSmallIntegerField(default=3, help_text='Interval between campaigns (in days).')

    # States
    is_active = models.BooleanField(default=True)
    is_active_on_sunday = models.BooleanField(default=True)
    sunday_start_time = models.CharField(max_length=255, choices=TIME_CHOICES, blank=True)
    is_active_on_monday = models.BooleanField(default=True)
    monday_start_time = models.CharField(max_length=255, choices=TIME_CHOICES, blank=True)
    is_active_on_tuesday = models.BooleanField(default=True)
    tuesday_start_time = models.CharField(max_length=255, choices=TIME_CHOICES, blank=True)
    is_active_on_wednesday = models.BooleanField(default=True)
    wednesday_start_time = models.CharField(max_length=255, choices=TIME_CHOICES, blank=True)
    is_active_on_thursday = models.BooleanField(default=True)
    thursday_start_time = models.CharField(max_length=255, choices=TIME_CHOICES, blank=True)
    is_active_on_friday = models.BooleanField(default=True)
    friday_start_time = models.CharField(max_length=255, choices=TIME_CHOICES, blank=True)
    is_active_on_saturday = models.BooleanField(default=True)
    saturday_start_time = models.CharField(max_length=255, choices=TIME_CHOICES, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'

    def get_current_campaign_message(self):
        # TODO:make me stylish
        # msgs = self.messages.order_by('id')
        # return msgs[self.current_message_index] if self.current_message_index <= msgs.count() else msgs.first()
        try:
            message = self.messages.order_by('id')[self.current_message_index]
        except IndexError:
            message = self.messages.order_by('id').first()

        return message

    def deactivate_campaign(self):
        self.current_message_index = 0
        self.is_active = False
        self.save(update_fields=['is_active', 'current_message_index'])
        self.recipients.update(processed=False)

    def deactivate_recipients(self):
        for r in self.recipients.all():
            r.processed = False
            r.save(update_fields=['processed'])


class Message(models.Model):
    campaign = models.ForeignKey(Campaign, related_name='messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, help_text=message_subject_help_text)
    text = RichTextUploadingField(help_text=message_text_help_text)
    opened = models.PositiveSmallIntegerField(default=0, editable=False)
    replied = models.PositiveSmallIntegerField(default=0, editable=False)
    total_sent = models.PositiveSmallIntegerField(default=0, editable=False)

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return self.subject


class Recipient(models.Model):
    campaign = models.ForeignKey(Campaign, related_name='recipients', on_delete=models.CASCADE)
    spreadsheet = models.ForeignKey('spreadsheets.Spreadsheet', related_name='recipients',
                                    blank=True, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    snippet_1 = models.CharField(max_length=255, blank=True)
    snippet_2 = models.CharField(max_length=255, blank=True)
    snippet_3 = models.CharField(max_length=255, blank=True)
    bounced = models.BooleanField(default=False)
    opened_message = models.BooleanField(default=False)
    replied = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    next_processed_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.email

    @property
    def status(self):
        return f'bounced: {self.bounced} | opened_message: {self.opened_message} | ' \
               f'processed: {self.processed} | replied: {self.replied}'

    class Meta:
        verbose_name = 'Recipient'
        verbose_name_plural = 'Recipients'


class Mailbox(models.Model):
    owner = models.ForeignKey(User, related_name='mailboxes', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True,
                                 help_text='Parameter will be used as "from" name. Example: Mr. Black.')
    use_tls = models.BooleanField(default=True)
    fail_silently = models.BooleanField(default=False)
    host = models.CharField(max_length=30, default='smtp.gmail.com')
    port = models.PositiveSmallIntegerField(default=587)
    host_user = models.CharField(max_length=255, unique=True,
                                 help_text="Your email address. Example: example@gmail.com.")
    host_password = models.CharField(max_length=255, help_text="Your password for email address account.")

    def __str__(self):
        return self.host_user

    class Meta:
        verbose_name = 'Mailbox'
        verbose_name_plural = 'Mailboxes'
