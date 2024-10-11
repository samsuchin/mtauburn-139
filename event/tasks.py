from celery import shared_task
import time
from valid.celery import app
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.core.validators import validate_email
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging



@shared_task
def continuous_outreach_task(event_pk, host_url):
    from event.models import Event
    from django.urls import reverse
    from django.templatetags.static import static
    from django.utils import timezone
    from django.core.mail import send_mail
    from urllib.parse import urljoin
    from django.core.exceptions import ValidationError
    import logging
    from django.conf import settings
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    from twilio.rest import Client

    event = Event.objects.get(pk = event_pk)
    for attendee in event.attendees.filter(invite_sent=False).order_by("-is_valid"):
        event.refresh_from_db()
        if not event.outreach_active:
            break
        location = reverse("display", kwargs={"uid": attendee.uid})
        display_link = urljoin(host_url, location.lstrip('/'))
        subject = "You're Invited"
        values = {
            'name': attendee.name,
            'event_name': event.name,
            'code': display_link
        }
    
        body = event.email_template.format(**values)

        if attendee.email:
            try:
                body = body.replace("\n", "<br>")

                message = Mail(
                from_email = settings.DEFAULT_FROM_EMAIL,
                to_emails=attendee.email,
                subject=event.email_subject,
                html_content=body)
                print(message)

                sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                print(sg)
                response = sg.send(message)
            except Exception as error:
                logging.error(error)
                print(error)
                logging.error(f"Error sending email to {attendee.email} for event {event.name}")
                attendee.is_valid = False
                attendee.save()
                continue
        elif attendee.phone_number:
            try:
                account_sid = settings.TWILIO_ACCOUNT_SID
                auth_token = settings.TWILIO_AUTH_TOKEN
                client = Client(account_sid, auth_token)
                message = client.messages.create(
                                    body=body,
                                    from_='+18336576712',
                                    to=f'+1{attendee.phone_number}'
                                )
                print(message)
                print(message.sid)
            except Exception as e:
                logging.error("error sending text: ", error)
                print("error sending text: ", error)
                attendee.is_valid = False
                attendee.save()
                continue
        else:
            logging.error("Attendee doesn't have a phone or email", error)
            print("Attendee doesn't have a phone or email: ", error)
            attendee.is_valid = False
            attendee.save()
            continue

        attendee.invite_sent = True
        attendee.invite_sent_at = timezone.now()
        attendee.is_valid = True
        attendee.save()

    event.outreach_active = False
    event.save()
    return "Outreach task completed."


# Earlier version used at Crimson
# @shared_task
# def continuous_outreach_task(event_pk, host_url):
#     from event.models import Event
#     from django.urls import reverse
#     from django.templatetags.static import static
#     from django.utils import timezone
#     from django.core.mail import send_mail
#     from urllib.parse import urljoin
#     from django.core.exceptions import ValidationError
#     import logging

#     event = Event.objects.get(pk = event_pk)
#     for attendee in event.attendees.filter(invite_sent=False).order_by("-is_valid"):
#         event.refresh_from_db()
#         if not event.outreach_active:
#             break
#         try:
#             validate_email(attendee.contact)
#             location = reverse("display", kwargs={"uid": attendee.uid})
#             # display_link = f"{host_url}{location}"
#             display_link = urljoin(host_url, location.lstrip('/'))
#             subject = "You're Invited"
#             values = {
#                 'name': attendee.name,
#                 'event_name': event.name,
#                 'code': display_link
#             }
        
#             body = event.email_template.format(**values)
        
#             from_email = settings.DEFAULT_FROM_EMAIL
#             recipient_list = [attendee.contact,]
            
#             send_mail(subject, body, from_email, recipient_list)
#             attendee.invite_sent = True
#             attendee.invite_sent_at = timezone.now()
#             attendee.is_valid = True
#             attendee.save()
#         except ValidationError as error:
#             logging.error(error)
#             print(error)
#             logging.error(f"Error sending email to {attendee.contact} for event {event.name}")
#             attendee.is_valid = False
#             attendee.save()

#     event.outreach_active = False
#     event.save()
#     return "Outreach task completed."

# @shared_task
# def send_email_task(attendee_pk, email_content):
#     from event.models import Attendee
#     from django.urls import reverse
#     from django.templatetags.static import static
#     attendee = Attendee.objects.get(pk = attendee_pk)
#     event = attendee.event


#     if event.image:
#         static_path = static("images/hallospee.jpg")
#         full_static_url = f"{host_url}{static_path}"
#     # Note: Change your template to be .html instead of .txt to support HTML content
#     body_html = render_to_string("emails/speedsm-invite.html", {
#         "display_link": display_link,
#         "img_url": full_static_url,
#         "name": attendee.name
#     })
            
#     email = EmailMultiAlternatives(
#         subject,
#         body_html,
#         settings.DEFAULT_FROM_EMAIL,
#         recipient_list
#     )
#     email.mixed_subtype = 'related'
#     email.attach_alternative(body_html, "text/html")
#     email.send()


# @shared_task
# def send_email_task(attendee_pk, host_url):
#     from event.models import Attendee
#     from django.urls import reverse
#     from django.templatetags.static import static
#     attendee = Attendee.objects.get(pk = attendee_pk)
#     event = attendee.event

#     location = reverse("display", kwargs={"uid": attendee.uid})
#     display_link = f"{host_url}{location}"

#     if event.image:
#         static_path = static("images/hallospee.jpg")
#         full_static_url = f"{host_url}{static_path}"
#     # Note: Change your template to be .html instead of .txt to support HTML content
#     body_html = render_to_string("emails/speedsm-invite.html", {
#         "display_link": display_link,
#         "img_url": full_static_url,
#         "name": attendee.name
#     })
            
#     email = EmailMultiAlternatives(
#         subject,
#         body_html,
#         settings.DEFAULT_FROM_EMAIL,
#         recipient_list
#     )
#     email.mixed_subtype = 'related'
#     email.attach_alternative(body_html, "text/html")
#     email.send()