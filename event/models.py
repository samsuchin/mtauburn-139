from django.utils import timezone
from django.db import models
import uuid
from . import EVENT
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
class Event(models.Model):
    uid = models.UUIDField(default=uuid.uuid4)
    name = models.CharField(max_length=50)
    description = models.TextField(null = True, blank=True)
    image = models.ImageField(upload_to='event_images', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    password = models.CharField(max_length=50)
    last_scanned = models.ForeignKey('Attendee', on_delete=models.SET_NULL, related_name='last_scanned', null=True, blank=True)
    email_template = models.TextField(default = EVENT.DEFAULT_INVITE_TEMPLATE)
    email_subject = models.CharField(default="You're Invited")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = "owned_events", null=True, blank=True)
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL)
    fake_number = models.IntegerField(null=True, blank=True)

    outreach_active = models.BooleanField(default = False)

    def __str__(self):
        return self.name
    
    def scan_count(self):
        return self.attendees.filter(scanned=True).count()

    def invites_sent(self):
        return self.attendees.filter(invite_sent = True).count()

    def total_invites(self):
        if self.fake_number:
            return self.fake_number
        return self.attendees.all().count()
    
    def outreach_percent(self):
        return int(self.invites_sent() / self.total_invites() * 100) if self.total_invites() > 0 else 0
    
    def scanned_percent(self):
        return int(self.scan_count() / self.total_invites() * 100) if self.total_invites() > 0 else 0
    
# class Person(models.Model):
#     email = models.EmailField(unique=True)
#     photo = models.ImageField(upload_to='people_images', null=True, blank=True)
#     name = models.CharField(max_length=200, null = True, blank = True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.name}"
    
#     def name(self):
#         return f"{self.name} {self.last_name}"

class Attendee(models.Model):
    uid = models.UUIDField(default=uuid.uuid4)
    name = models.CharField(max_length=200, null = True, blank = True)
    email = models.EmailField(null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    status = models.CharField(max_length=50, default="Default")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attendees")
    created_at = models.DateTimeField(auto_now_add=True)
    scanned = models.BooleanField(default=False)
    scanned_at = models.DateTimeField(null=True, blank=True)
    invite_sent = models.BooleanField(default=False)
    invite_sent_at = models.DateTimeField(null=True, blank=True)
    is_valid = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    def get_contact(self):
        if self.email:
            return self.email
        return self.phone_number

    def scan(self):
        self.scanned = True
        self.scanned_at = timezone.now()
        self.save()
    
    def get_status(self, event_pk):
        if int(self.event.pk) == int(event_pk):
            # if self.type == "blacklist":
            #     return "invalid"
            if self.scanned:
                return "scanned"
            return "valid"
        return "invalid"

    def scan_info(self):
        return f"{self.name} @ {self.scanned_at}"
    
class Error(models.Model):
    created_at = models.DateTimeField(auto_now_add = True)
    message = models.TextField(max_length=1000)
    event = models.ForeignKey(Event, on_delete = models.CASCADE, related_name="timelines")

    def __str__(self) -> str:
        return self.message