from django.shortcuts import render, redirect, get_object_or_404
from .models import Productor, CodigoProductor
from AseguradoraApp.models import Cia
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse

@login_required(login_url='/login/login/')
def vista_productores(req):
    productores = Productor.objects.all()
    return render(req,"ProductorApp/productores.html", {"productores": productores})

@login_required(login_url='/login/login/')
def vista_add_productor(req:HttpRequest)->HttpResponse:
    if req.method == 'POST':
        nombre = req.POST.get('nombre')
        dni = req.POST.get('dni')
        condicion_iva = req.POST.get('condicion_iva')
        matricula = req.POST.get('matricula')
        email = req.POST.get('email','')
        telefono = req.POST.get('telefono','')
        direccion = req.POST.get('direccion','')
        Productor.objects.create(
            nombre = nombre,
            dni = dni,
            condicion_iva = condicion_iva,
            matricula = matricula,
            email = email,
            telefono = telefono,
            direccion = direccion,
        )
        return redirect('productores')
    return redirect('productores')

@login_required(login_url='/login/login/')
def vista_edit_productor(req:HttpRequest, id):
    productor = get_object_or_404(Productor, id=id)
    codigos = CodigoProductor.objects.filter(productor_id=id)
    aseguradoras = Cia.objects.all()
    if req.method == 'POST':
        productor.nombre = req.POST.get('nombre')
        productor.dni = req.POST.get('dni')
        productor.condicion_iva = req.POST.get('condicion_iva')
        productor.matricula = req.POST.get('matricula')
        productor.email = req.POST.get('email','')
        productor.telefono = req.POST.get('telefono','')
        productor.direccion = req.POST.get('direccion','')
        productor.save()
        return redirect('productores')
    cond_choices = productor._meta.get_field('condicion_iva').choices
    return render(req,"ProductorApp/productores_edit.html", {
        "productor": productor, 
        "aseguradoras": aseguradoras,
        "cond_choices": cond_choices,
        "codigos": codigos})

@login_required(login_url='/login/login/')
def vista_delete_productor(req:HttpRequest, id):
    productor = get_object_or_404(Productor, id=id)
    productor.delete()
    return redirect('productores')

@login_required(login_url='/login/login/')
def vista_add_codigo(req:HttpRequest)->HttpResponse:
    if req.method == 'POST':
        idproductor = req.POST.get('productorid')
        codigo = req.POST.get('codigo')
        idaseguradora = req.POST.get('aseguradora')
        descripcion = req.POST.get('descripcion')
        CodigoProductor.objects.create(
            productor = get_object_or_404(Productor, id=idproductor),
            codigo = codigo,
            aseguradora = get_object_or_404(Cia, id=idaseguradora),
            descripcion = descripcion,
            activo = True
        )
        return redirect('edit_productor', id=idproductor)
    return redirect('productores')

@login_required(login_url='/login/login/')
def vista_toggle_codigo(req:HttpRequest, id)->HttpResponse:
    codigo = get_object_or_404(CodigoProductor, id=id)
    prod_id = codigo.productor.id
    codigo.activo = not codigo.activo
    print("Toggle efectuado")
    codigo.save()
    return redirect('edit_productor', id=prod_id)

@login_required(login_url='/login/login/')
def vista_edit_codigo(req:HttpRequest, id)->HttpResponse:
    codigo = get_object_or_404(CodigoProductor, id=id)
    prod_id = codigo.productor.id
    if req.method == 'POST':
        codigo.codigo = req.POST.get('edit_codigo')
        codigo.descripcion = req.POST.get('edit_descripcion')
        codigo.save()
        return redirect('edit_productor', id=prod_id)
    return redirect('edit_productor', id=prod_id)
