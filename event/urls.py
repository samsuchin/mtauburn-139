from django.urls import path
from .views import *

urlpatterns = [
    path("display/<uid>/", display, name="display"),
    path("check-password", check_password, name="check_password"),
    path("manage/<pk>/", manage_event, name="manage_event"),
    path("send-codes/<event_pk>/", send_codes, name="send_codes"),
    path("update-attendee/", update_attendee, name="update_attendee"),
    path("add-invite/<event_pk>/", add_invite, name="add_invite"),
    path("upload-invites/<event_pk>/", upload_invites, name="upload_invites"),
    path("send-invites/<event_pk>/", send_codes, name="send_invites"),
    path("save-event/<event_pk>/", save_event, name="save_event"),
    path("start-outreach/<event_pk>/", start_outreach, name="start_outreach"),
    path("stop-outreach/<event_pk>/", stop_outreach, name="stop_outreach"),
    path("attend/<event_pk>/", attend, name="attend")
]
