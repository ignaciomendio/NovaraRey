from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login  
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages


def vista_logout(req):
    logout(req)
    return redirect("home")

def vista_login(req):
    form = AuthenticationForm(req, data=req.POST or None)
    form.fields['username'].widget.attrs.update({'class': 'form-control'})
    form.fields['password'].widget.attrs.update({'class': 'form-control'})
    if req.method == "POST":
        if form.is_valid():
            user = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            usuario = authenticate(username=user, password=password)
            if not req.POST.get("remember_me"):
                req.session.set_expiry(0)  # expira al cerrar navegador
            if usuario is not None:
                login(req, usuario)
                redirect_to = req.GET.get("next", "home")
                return redirect(redirect_to)
            else:
                messages.error(req, "Credenciales inválidas.")
        else:
            messages.error(req, "Formulario inválido.")
    return render(req, "AuthApp/login.html", {"form": form})