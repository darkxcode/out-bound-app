from django.http import HttpResponse
from .models import Recipient


def open_message_tracker(request, contact_email):
    contact = Recipient.objects.get(email=contact_email)
    contact.open_message = True
    contact.save()
    with open("/home/ubuntu/mailer/static/img/000000-1.png", "rb") as f:
        return HttpResponse(f.read(), content_type="image/png")
