from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login  
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages


def vista_logout(req):
    logout(req)
    return redirect("home")

def vista_login(req):
    if req.method=="POST":
        form = AuthenticationForm(req, data=req.POST)
        if form.is_valid():
            user=form.cleaned_data.get("username")
            password=form.cleaned_data.get("password")
            usuario=authenticate(username=user, password=password)
            if usuario:
                login(req,usuario)
                return redirect("home")
            else:
                messages.error(req, "Usuario no Valido")
                form = AuthenticationForm()
                return render(req, "AuthApp/login.html", {"form": form})
        else:
            messages.error(req, "Usuario no Valido")
            form = AuthenticationForm()
            return render(req, "AuthApp/login.html", {"form": form})
    else:
        form = AuthenticationForm()
        return render(req, "AuthApp/login.html", {"form": form})