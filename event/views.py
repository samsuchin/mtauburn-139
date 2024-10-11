from typing import Any, Dict
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render, HttpResponse
from django.urls import reverse
from event.models import Attendee, Event
from django.http import JsonResponse
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic.edit import UpdateView
from django.utils.decorators import method_decorator
from . import EVENT
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives, get_connection
from django.views.decorators.csrf import csrf_exempt
import json
import csv
from django.templatetags.static import static
import os
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .tasks import continuous_outreach_task
from django.contrib import messages
from .utils import *
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from django.db.models import Q
import chardet

@login_required
def all_events(request):
    my_events = Event.objects.filter(Q(admins=request.user) | Q(owner=request.user)).order_by("-created_at")
    # other_events = Event.objects.filter(admins=request.user).order_by("-created_at")
    # my_events = Event.objects.filter(owner=request.user).order_by("-created_at")
    if request.user.is_staff:
        my_events = Event.objects.all().order_by("-created_at")

    context = {
        "my_events": my_events,
        # "other_events": other_events
    }
    return render(request, "events.html", context)

def display(request, uid):
    attendee = get_object_or_404(Attendee, uid=uid)
    context = {
        "attendee": attendee
    }
    return render(request, "display_code.html", context)

def check_password(request):
    data = request.GET
    event_pk = data.get("event_pk")
    password = data.get("password")
    event = get_object_or_404(Event, pk=event_pk)
    if event.password == password:
        data = {
            "status": "valid"
        }
    else:
        data = {
            "status": "invalid"
        }
    return JsonResponse(data, safe=False)


class ManageEvent(UpdateView):
    model = Event
    template_name = "manage_event.html"
    fields = ["name", "password"]
    def get_success_url(self):
        return self.request.path
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['attendees'] = self.object.attendees.all()
        data["attendee_types"] = EVENT.PEOPLE_CHOICES
        return data

def manage_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    user = request.user
    if user.is_staff or user.is_superuser or user == event.owner or user in event.admins.all():
        context = {
            "event": event,
            "attendees": event.attendees.all().order_by("is_valid", "name"),
            "attendee_types": EVENT.PEOPLE_CHOICES
        }
        return render(request, "manage_event.html", context)

# def send_codes(request, event_pk):
#     event = get_object_or_404(Event, pk=event_pk)
#     subject = event.name
#     if request.user.is_staff or request.user.is_superuser:
#         attendees = event.attendees.filter(invite_sent=False)
#         messages = []
#         for attendee in attendees:
#             location = reverse("display", kwargs={"uid": attendee.uid})
#             display_link = request.build_absolute_uri(location)
#             body = render_to_string("emails/invite.txt", {"display_link": display_link})
#             message = (
#                 subject,
#                 body,
#                 settings.DEFAULT_FROM_EMAIL,
#                 [attendee.email],
#             )
#             messages.append(message)
#         send_mass_mail(tuple(messages))
#         attendees.update(invite_sent=True)
#         return HttpResponse("Success", status=201) 
#     return HttpResponse("Error", status=404) 

from django.core.mail import EmailMultiAlternatives

import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def stop_outreach(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    event.outreach_active = False
    event.save()
    return redirect("manage_event", pk = event_pk)



def start_outreach(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    user = request.user
    print("working")
    if user.is_staff or user.is_superuser or user == event.owner or user in event.admins.all():
        template = event.email_template

        # Define expected placeholders
        expected_placeholders = ['name', 'event_name', 'code']

        # Find and correct typos in placeholders
        typo_corrections = find_typo_placeholders(template, expected_placeholders)
        if typo_corrections:
            # Notify the user about typos and suggested corrections
            typo_messages = [f"Did you mean '{v}' instead of '{k}'?" for k, v in typo_corrections.items()]
            messages.error(request, " ".join(typo_messages))
            return redirect("manage_event", pk = event_pk)


        if not validate_template(template):
            messages.error(request, "Email template contains unmatched curly braces.")
            return redirect("manage_event", pk = event_pk)
        
        if '{code}' in template:
            # Use 'request.build_absolute_uri()' to get the full base URL
            host_url = request.build_absolute_uri('/')

            continuous_outreach_task.delay(event.pk, host_url)
            event.outreach_active = True
            event.save()
            messages.success(request, "Outreach process started successfully.")
        else:
            messages.error(request, "Email template is missing the required {code} placeholder.")
    else:
        messages.error(request, "You do not have permission to start the outreach for this event.")
    
    return redirect("manage_event", pk = event_pk)

def send_codes(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    subject = event.name
    
    if request.user.is_staff or request.user.is_superuser:
        attendees = event.attendees.filter(invite_sent=False)[:10]
        messages = []
        
        for attendee in attendees:
            location = reverse("display", kwargs={"uid": attendee.uid})
            display_link = request.build_absolute_uri(location)
            static_path = static("images/hallospee.jpg")
            full_static_url = request.build_absolute_uri(static_path)
            # Note: Change your template to be .html instead of .txt to support HTML content
            body_html = render_to_string("emails/speedsm-invite.html", {
                "display_link": display_link,
                "img_url": full_static_url,
                "name": attendee.name
            })
            
            email = EmailMultiAlternatives(
                subject,
                body_html,
                settings.DEFAULT_FROM_EMAIL,
                [attendee.email]
            )
            print(f"{attendee.name} - {attendee.email}")
            email.mixed_subtype = 'related'
            email.attach_alternative(body_html, "text/html")
            img_dir = "static/images/"
            image = "hallospee.jpg"
            file_path = os.path.join(img_dir, image)
            # with open(file_path, 'rb') as f:
            #     img = MIMEImage(f.read())
            #     img.add_header('Content-ID', '<hallospee>')
            #     img.add_header('Content-Disposition', 'inline', filename=image)
            # email.attach(img)
            email.send()
            attendee.invite_sent = True
            attendee.invite_sent_at = timezone.now()
            attendee.save()

        return HttpResponse("Success", status=201)

    return HttpResponse("Error", status=404)


# def send_codes(request, event_pk):
#     event = get_object_or_404(Event, pk=event_pk)
#     subject = event.name
    
#     if request.user.is_staff or request.user.is_superuser:
#         attendees = event.attendees.filter(invite_sent=False)
#         n = 40
#         for i in range(0, len(attendees), n):
#             temp_send_to = attendees[i:i+n]
                
#             messages = []
#             connection = get_connection()
#             connection.open()
#             for attendee in temp_send_to:
#                 location = reverse("display", kwargs={"uid": attendee.uid})
#                 display_link = request.build_absolute_uri(location)
#                 static_path = static("images/speekonos.jpg")
#                 full_static_url = request.build_absolute_uri(static_path)
#                 # Note: Change your template to be .html instead of .txt to support HTML content
#                 body_html = render_to_string("emails/invite.html", {
#                     "display_link": display_link,
#                     "img_url": full_static_url
#                 })
                
#                 email = EmailMultiAlternatives(
#                     subject,
#                     body_html,  # This will be the plain text version, maybe strip tags or provide alternate content.
#                     settings.DEFAULT_FROM_EMAIL,
#                     [attendee.email]
#                 )
#                 print(attendee.email)
#                 email.mixed_subtype = 'related'
#                 email.attach_alternative(body_html, "text/html")
#                 img_dir = "static/images/"
#                 image = "speekonos.jpg"
#                 file_path = os.path.join(img_dir, image)
#                 with open(file_path, 'rb') as f:
#                     img = MIMEImage(f.read())
#                     img.add_header('Content-ID', '<speekonos>')
#                     img.add_header('Content-Disposition', 'inline', filename=image)
#                 email.attach(img)
#                 messages.append(email)
            
#             connection.send_messages(messages)
#             # for email in messages:
#             #     email.send()
#             connection.close()
#             print("New group sent: ", temp_send_to)
#         attendees.update(invite_sent=True)
#         return HttpResponse("Success", status=201)

#     return HttpResponse("Error", status=404)

@csrf_exempt
def update_attendee(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print(data)
        action = data.get("action")
        attendee = get_object_or_404(Attendee, pk = data.get("pk"))
        print(action)
        if action == "status":
            status = data.get("status")
            attendee.status = status
            attendee.save()
            return HttpResponse("Updated - Status", status=201)
        elif action == "remove":
            attendee.delete()
            return HttpResponse("Deleted", status=201)  
        
        elif action == "email":
            email = data.get("email")
            attendee.email = email
            attendee.save()
            return HttpResponse("Updated - Email", status=201)  
        
    return HttpResponse("Error", status = 404)


def add_invite(request, event_pk):
    if request.method == "POST":
        data = request.POST
        print(data)
        contact = data.get("contact").strip()
        name = data.get("name").strip()
        status = data.get("status").strip()
        event = get_object_or_404(Event, pk=event_pk)

        email, phone_number = None, None

        if "@" in contact:
            try:
                validate_email(contact)
                email = contact
            except ValidationError:
                messages.error(request, f"The email {contact} is invalid.")
                return redirect("manage_event", pk=event_pk)
        else:
            normalized_phone = re.sub("[^\d]", "", contact)
            if len(normalized_phone) != 10:
                messages.error(request, f"The phone number {contact} was invalid.")
                return redirect("manage_event", pk=event_pk)
            phone_number = normalized_phone

        if email:
            attendee, created = Attendee.objects.get_or_create(email=email, event=event)
        elif phone_number:
            attendee, created = Attendee.objects.get_or_create(phone_number=phone_number, event=event)
        
        if created:
            attendee.name = name
            attendee.status = status
            attendee.save()
            messages.success(request, "Invite added.")
        else:
            messages.error(request, "This invite already exists.")

        return redirect("manage_event", pk=event_pk)



def upload_invites(request, event_pk):
    if request.method == "POST":
        csv_file = request.FILES["file"]
        event = get_object_or_404(Event, pk=event_pk)

    
        # Read a sample of the file to detect encoding
        sample = csv_file.read(10000)
        result = chardet.detect(sample)
        encoding = result['encoding']

        # Ensure that an encoding was detected
        if encoding is None:
            encoding = 'utf-8'  # Default to utf-8 if chardet fails to detect

        # Reset file read position to the start
        csv_file.seek(0)

        # !!!!!!!
        # Repalce ’ with '
        # !!!!!!!1


        
        # Read and decode the file with the detected or default encoding
        decoded_file = csv_file.read().decode(encoding)

        # Process CSV file
        reader = csv.reader(decoded_file.splitlines())
        
        for row in reader:
            name, contact, status = row
            contact = contact.strip()
            name = name.strip()
            status = status.strip()

            email, phone_number = None, None

            if "@" in contact:  # Process as email
                try:
                    validate_email(contact)
                    email = contact
                except ValidationError:
                    messages.error(request, f"The email {contact} is invalid.")
                    continue  # Skip to the next row
            else:  # Process as phone number
                normalized_phone = re.sub("[^\d]", "", contact)
                if len(normalized_phone) != 10:
                    messages.error(request, f"The phone number {contact} was invalid.")
                    continue  # Skip to the next row
                phone_number = normalized_phone

            if email:
                attendee, created = Attendee.objects.get_or_create(email=email, event=event)
            elif phone_number:
                attendee, created = Attendee.objects.get_or_create(phone_number=phone_number, event=event)

            if created:
                attendee.name = name
                attendee.status = status
                attendee.save()

        messages.success(request, "Invites uploaded successfully.")
        return redirect("manage_event", pk=event_pk)

def save_event(request, event_pk):
    if request.method == "POST":
        print(request.body)
        event = get_object_or_404(Event, pk = event_pk)
        data = json.loads(request.body)
        name = data.get("name")
        password = data.get("password")
        email_template = data.get("email_template")
        email_subject = data.get("email_subject")
        event.name = name
        event.password = password
        event.email_template = email_template
        event.email_subject = email_subject
        
        event.save()
        return HttpResponse("saved", status=200)
    return HttpResponse("error", status=404)


def attend(request, event_pk):
    event = get_object_or_404(Event, pk = event_pk)
    if request.method == "POST":
        data = request.POST
        contact = data.get("email-phone").strip()
        name = data.get("name").strip()

        email, phone_number = None, None

        if "@" in contact:
            try:
                validate_email(contact)
                email = contact
            except ValidationError:
                messages.error(request, f"The email {contact} is invalid.")
                return redirect("manage_event", pk=event_pk)
        else:
            normalized_phone = re.sub("[^\d]", "", contact)
            if len(normalized_phone) != 10:
                messages.error(request, f"The phone number {contact} was invalid.")
                return redirect("manage_event", pk=event_pk)
            phone_number = normalized_phone

        if email:
            attendee, created = Attendee.objects.get_or_create(email=email, event=event)
        elif phone_number:
            attendee, created = Attendee.objects.get_or_create(phone_number=phone_number, event=event)
        
        if created:
            attendee.name = name
            attendee.save()
            messages.success(request, "Invite added.")
    context = {
        "event": event
    }
    return render(request, "attend.html", context)