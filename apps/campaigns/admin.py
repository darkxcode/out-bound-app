from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps.campaigns.forms import CampaignForm, MessageForm, MailboxForm
from apps.campaigns.models import Campaign, Message, Mailbox, Recipient


class MessageInline(admin.StackedInline):
    model = Message
    form = MessageForm
    extra = 1


class RecipientOpenedInline(admin.StackedInline):
    model = Recipient
    extra = 0
    fields = ['recipient']
    readonly_fields = ['recipient']
    verbose_name_plural = 'Recipients who opened message'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(opened_message=True)

    @staticmethod
    def recipient(instance):
        url = reverse("admin:campaigns_recipient_change", args=(instance.id,))
        name = f'{instance.email}: {instance.status}'
        return mark_safe(f'<a href="{url}">{name}</a>')


class RecipientRepliedInline(admin.StackedInline):
    model = Recipient
    extra = 0
    fields = ['recipient']
    readonly_fields = ['recipient']
    verbose_name_plural = 'Recipients who replied message'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(replied=True)

    @staticmethod
    def recipient(instance):
        url = reverse("admin:campaigns_recipient_change", args=(instance.id,))
        name = f'{instance.email}: {instance.status}'
        return mark_safe(f'<a href="{url}">{name}</a>')


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    form = CampaignForm
    inlines = [MessageInline, RecipientOpenedInline, RecipientRepliedInline]
    list_display = ('name', 'is_active', 'recipients', 'processed', 'opened', 'bounced', 'replied', 'messages_sent',
                    'daily_limit', 'sunday_start_time', 'monday_start_time', 'tuesday_start_time',
                    'wednesday_start_time', 'thursday_start_time', 'friday_start_time', 'saturday_start_time')

    search_fields = ('name', )

    def queryset(self, request):
        qs = super(CampaignAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(creator=request.user)

    @staticmethod
    def recipients(obj):
        return obj.recipients.count()

    @staticmethod
    def processed(obj):
        return obj.recipients.filter(processed=True).count()

    @staticmethod
    def opened(obj):
        return obj.recipients.filter(opened_message=True).count()

    @staticmethod
    def bounced(obj):
        return obj.recipients.filter(bounced=True).count()

    @staticmethod
    def replied(obj):
        return obj.recipients.filter(replied=True).count()

    @staticmethod
    def messages_sent(obj):
        return obj.total_messages_counter

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.creator = request.user
        form.save()


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    pass


@admin.register(Mailbox)
class MailboxAdmin(admin.ModelAdmin):
    form = MailboxForm

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.owner = request.user
        instance.save()
