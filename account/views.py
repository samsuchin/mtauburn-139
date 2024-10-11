from email import message
from importlib.metadata import requires
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.messages import error
from .forms import SignUpForm
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.contrib import messages
from . import ACCOUNT

def signup(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            referral_code = request.POST.get("referral", None)
            # request.session['django_timezone'] = request.POST.get('timezone')
            account = form.save()
            account.send_confirmation_email(request)
            # account.is_active = True
            # account.save()
            # login(request, account)
            # messages.success(request, "BuyXR Account Activated!")
            messages.success(request, f"Check {account.email}'s inbox to activate your account!")
            print("message sent")
            return redirect("index")
    context = {
        "form": form,
        'timezones': ACCOUNT.common_timezones
    }
    return render(request, "registration/signup.html", context)

def activate_account(request, token):
    user = get_object_or_404(get_user_model(), activation_key = token)
    user.is_active = True
    user.save()
    login(request, user)
    messages.success(request, "Account Activated!")
    return redirect("index")