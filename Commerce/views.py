from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect

# Create your views here.
def index(request):
    return render(request, 'index.html')

def register(request):
     if request.method == "POST":
          username = request.POST["username"]
          email = request.POST["email"]
          password = request.POST["password"]
          confirmation = request.POST["confirmation"]
          if password != confirmation:
               return render(request, "register.html", {
                    "message": "Passwords do not match"
               })
          
          try:
               user = User.objects.create_user(username, email, password)
               user.save()
          except IntegrityError:
               return render(request, "register.html", {
                    "messagey": "Username already taken."
               })
          login(request, user)
          return HttpResponseRedirect(reverse("index"))
     else:
          return render(request,"register.html")

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username,password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "login.html")

def logout(request):
     logout(request)
     return render(request, "login.html")
