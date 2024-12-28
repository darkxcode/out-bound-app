import imaplib

from django import forms

from apps.campaigns.models import Campaign, Message, Mailbox


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        exclude = ('creator', 'total_messages_counter', 'current_message_index')


class MessageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].widget = forms.TextInput(attrs={'size': '107'})

    class Meta:
        model = Message
        exclude = ('opened', 'replied', 'total_sent')


class MailboxForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['host_password'].widget = forms.PasswordInput()

    def clean(self):
        cleaned_data = self.cleaned_data
        try:
            mailbox = imaplib.IMAP4_SSL(cleaned_data['host'])
            mailbox.login(cleaned_data['host_user'], cleaned_data['host_password'])
            mailbox.select()
            mailbox.close()
            mailbox.logout()
        except Exception:
            raise forms.ValidationError('Incorrect host user or host password. Only gmail addresses supported.')
        return cleaned_data

    class Meta:
        model = Mailbox
        exclude = ('owner', 'use_tls', 'fail_silently')
