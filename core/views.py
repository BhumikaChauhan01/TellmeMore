from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required


# ---------------- Registration ---------------- #
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard:dashboard")  # Redirect after successful register
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})


# ---------------- Public Pages ---------------- #
def home_view(request):
    return render(request, "home.html")

def about_view(request):
    return render(request, "about.html")

def how_to_view(request):
    return render(request, "how_to.html")

def contact_view(request):
    return render(request, 'contact_us.html')

