from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from event.models import Attendee, Event
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

def detect(request, uid):
    timezone.activate("America/New_York")
    context = {
        "event": get_object_or_404(Event, uid=uid),
        "scanned": Attendee.objects.filter(event__uid=uid, scanned=True).order_by("-scanned_at"),
        "not_scanned": Attendee.objects.filter(event__uid=uid, scanned=False).order_by("-name"),
    }
    return render(request, "detect.html", context)

@csrf_exempt
def get_status(request):
    data = request.GET
    uid = data.get("uid")
    event_pk = data.get("event_pk")
    try:
        attendee = get_object_or_404(Attendee, uid = uid)
        event = get_object_or_404(Event, pk = event_pk)
        if event.last_scanned == attendee:
            return JsonResponse({"status": "no-change"}, safe=False)

        status = attendee.get_status(event_pk)
        if status == "valid":
            attendee.scan()
        data = {
            "status": status,
            "tag": attendee.status,
            "name": attendee.name,
            "pk": attendee.pk,
            "scan_count": attendee.event.scan_count(),
            "scan_info": attendee.scan_info()
        }
        event.last_scanned = attendee
        event.save()
    except:
        data = {
            "status": "error",
        }
        
    return JsonResponse(data, safe=False)