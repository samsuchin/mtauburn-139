from django.urls import path
from .views import *

urlpatterns = [
    path("<uid>/", detect, name="detect"),
    path("get-status", get_status, name="get_status")
]
