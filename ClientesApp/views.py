from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Cliente, ClientePersonaFisica, ClientePersonaJuridica
from MainApp.models import Address, AdressType
from .models import TelefonoCte, EmailCte

@login_required(login_url='/login/login/')
def vista_clientes(request):
    filtro_nombre = request.GET.get('nombre', '').strip()
    filtro_identificador = request.GET.get('identificador', '').strip()
    filtro_tipo = request.GET.get('tipo', '')
    clientes_pf = ClientePersonaFisica.objects.filter(
        Q(nombre__icontains=filtro_nombre) | Q(apellido__icontains=filtro_nombre),
        dni__icontains=filtro_identificador
    )
    print(f'cantidad de clientes PF: {clientes_pf.count()}')
    clientes_pj = ClientePersonaJuridica.objects.filter(
        razon_social__icontains=filtro_nombre,
        cuit__icontains=filtro_identificador
    )
    print(f'cantidad de clientes PJ: {clientes_pj.count()}')
   
    if filtro_tipo == 'PF':
        clientes = list(clientes_pf)
    elif filtro_tipo == 'PJ':
        clientes = list(clientes_pj)
    else:
        clientes = list(clientes_pf) + list(clientes_pj)

    return render(request, 'ClientesApp/clientes_main.html', {
        'filtro_tipo': filtro_tipo,
        'filtro_nombre': filtro_nombre,
        'filtro_identificador': filtro_identificador,
        'clientes': clientes
    })

@login_required(login_url='/login/login/')
def cliente_edit(request, id):

    addtype_choices = AdressType.objects.all()
    # Primero intentamos con Persona Física
    cliente_pf = ClientePersonaFisica.objects.filter(id=id).first()
    if cliente_pf:
        # Si es POST, actualizamos
        if request.method == 'POST':
            cliente_pf.nombre = request.POST.get('nombre', cliente_pf.nombre)
            cliente_pf.apellido = request.POST.get('apellido', cliente_pf.apellido)
            cliente_pf.dni = request.POST.get('dni', cliente_pf.dni)
            cliente_pf.fecha_nacimiento = request.POST.get('fecha_nacimiento', cliente_pf.fecha_nacimiento)
            cliente_pf.condicion_iva = request.POST.get('condicion_iva', cliente_pf.condicion_iva)
            cliente_pf.notas = request.POST.get('notas', cliente_pf.notas)
            cliente_pf.save()

            direccion = cliente_pf.direccion
            if direccion:
                direccion.calle = request.POST.get('calle', direccion.calle)
                direccion.numero = request.POST.get('numero', direccion.numero)
                direccion.piso = request.POST.get('piso', direccion.piso)
                direccion.dpto = request.POST.get('dpto', direccion.dpto)
                direccion.localidad = request.POST.get('localidad', direccion.localidad)
                direccion.provincia = request.POST.get('provincia', direccion.provincia)
                direccion.cp = request.POST.get('cp', direccion.cp)
                direccion.tipo_id = request.POST.get('addtype', direccion.tipo_id)
                direccion.save()
            # tras guardar, redirigimos para evitar reenvío de formulario
            return redirect('clientes_main')
        
        telefonos = cliente_pf.telefonos.all()
        emails = cliente_pf.emails.all()
        cond_choices = cliente_pf._meta.get_field('condicion_iva').choices
        

        return render(request, 'ClientesApp/clientes_pf_edit.html', {
            'cliente': cliente_pf,
            'telefonos': telefonos,
            'emails': emails,
            'cond_choices': cond_choices,
            'addtype_choices': addtype_choices,	
        })

    # Si no es PF, debe ser Jurídica (o 404)
    cliente_pj = get_object_or_404(ClientePersonaJuridica, id=id)
    telefonos = cliente_pj.telefonos.all()
    emails = cliente_pj.emails.all()
    cond_choices = cliente_pj._meta.get_field('condicion_iva').choices

    if cliente_pj:
        # Si es POST, actualizamos
        if request.method == 'POST':
            cliente_pj.razon_social = request.POST.get('razon_social', cliente_pj.razon_social)
            cliente_pj.cuit = request.POST.get('cuit', cliente_pj.cuit)
            cliente_pj.condicion_iva = request.POST.get('condicion_iva', cliente_pj.condicion_iva)
            cliente_pj.notas = request.POST.get('notas', cliente_pj.notas)
            cliente_pj.save()

            direccion = cliente_pj.direccion
            if direccion:
                direccion.calle = request.POST.get('calle', direccion.calle)
                direccion.numero = request.POST.get('numero', direccion.numero)
                direccion.piso = request.POST.get('piso', direccion.piso)
                direccion.dpto = request.POST.get('dpto', direccion.dpto)
                direccion.localidad = request.POST.get('localidad', direccion.localidad)
                direccion.provincia = request.POST.get('provincia', direccion.provincia)
                direccion.cp = request.POST.get('cp', direccion.cp)
                direccion.tipo_id = request.POST.get('addtype', direccion.tipo_id)
                direccion.save()
            # tras guardar, redirigimos para evitar reenvío de formulario
            return redirect('clientes_main')
        
        telefonos = cliente_pj.telefonos.all()
        emails = cliente_pj.emails.all()
        cond_choices = cliente_pj._meta.get_field('condicion_iva').choices

    return render(request, 'ClientesApp/clientes_pj_edit.html', {
        'cliente': cliente_pj,
        'telefonos': telefonos,
        'emails': emails,
        'cond_choices': cond_choices,
        'addtype_choices': addtype_choices,
    })


def cliente_create(request, typ):
    addtype_choices = AdressType.objects.all()
    if typ == 'PF':
        cond_choices = ClientePersonaFisica._meta.get_field('condicion_iva').choices
        if request.method == 'POST':
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            dni = request.POST.get('dni')
            fecha_nacimiento = request.POST.get('fecha_nacimiento')
            condicion_iva = request.POST.get('condicion_iva')
            notas = request.POST.get('notas', '')
            direccion = Address.objects.create(
                calle=request.POST.get('calle'),
                numero=request.POST.get('numero'),
                piso=request.POST.get('piso', ''),
                dpto=request.POST.get('dpto', ''),
                localidad=request.POST.get('localidad'),
                provincia=request.POST.get('provincia'),
                cp=request.POST.get('cp'),
                tipo_id=request.POST.get('addtype')
            )
            cliente = ClientePersonaFisica.objects.create(
                nombre=nombre,
                apellido=apellido,
                dni=dni,
                fecha_nacimiento=fecha_nacimiento,
                condicion_iva=condicion_iva,
                notas=notas,
                direccion=direccion
            )
            return redirect('clientes_main')
        return render(request, 'ClientesApp/cliente_pf_create.html', 
                      {'cond_choices': cond_choices, 
                       'addtype_choices': addtype_choices})
    else:
        cond_choices = ClientePersonaJuridica._meta.get_field('condicion_iva').choices
        if request.method == 'POST':
            razon_social = request.POST.get('razon_social')
            cuit = request.POST.get('cuit')
            condicion_iva = request.POST.get('condicion_iva')
            notas = request.POST.get('notas', '')
            direccion = Address.objects.create(
                calle=request.POST.get('calle'),
                numero=request.POST.get('numero'),
                piso=request.POST.get('piso', ''),
                dpto=request.POST.get('dpto', ''),
                localidad=request.POST.get('localidad'),
                provincia=request.POST.get('provincia'),
                cp=request.POST.get('cp'),
                tipo_id=request.POST.get('addtype')
            )
            cliente = ClientePersonaJuridica.objects.create(
                razon_social=razon_social,
                cuit=cuit,
                condicion_iva=condicion_iva,
                notas=notas,
                direccion=direccion
            )
            return redirect('clientes_main')
        return render(request, 'ClientesApp/cliente_pj_create.html', 
                      {'cond_choices': cond_choices, 
                       'addtype_choices': addtype_choices})

def cliente_delete(request, id):
    pass

@login_required(login_url='/login/login/')
def cliente_edit_teladd(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        numero = request.POST.get('numero')
        contacto = request.POST.get('contactotel')
        descripcion = request.POST.get('descripcion', '')
        telefono = cliente.telefonos.create(numero=numero, contacto=contacto, descripcion=descripcion)
        return redirect('cliente_edit', id=cliente.id)
    return render(request, 'ClientesApp/cliente_edit_teladd.html', {'cliente': cliente})

@login_required(login_url='/login/login/')
def cliente_edit_mailadd(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        email = request.POST.get('email')
        contacto = request.POST.get('contactomail')
        descripcion = request.POST.get('descripcionMail', '')
        mail = cliente.emails.create(email=email, contacto=contacto, descripcion=descripcion)
        return redirect('cliente_edit', id=cliente.id)
    return render(request, 'ClientesApp/cliente_edit_mailadd.html', {'cliente': cliente})

@login_required(login_url='/login/login/')
def cliente_edit_teledit(request, id):
    telefono = get_object_or_404(TelefonoCte, id=id)
    if request.method == 'POST':
        telefono.numero = request.POST.get('numero', telefono.numero)
        telefono.contacto = request.POST.get('contacto', telefono.contacto)
        telefono.descripcion = request.POST.get('descripcion', telefono.descripcion)
        telefono.save()
        cliente = telefono.cliente_set.first()
        return redirect('cliente_edit', id=cliente.id)
    return render(request, 'ClientesApp/cliente_edit_teledit.html', {'telefono': telefono})

@login_required(login_url='/login/login/')
def cliente_edit_mailedit(request, id):
    email = get_object_or_404(EmailCte, id=id)
    if request.method == 'POST':
        email.email = request.POST.get('mail', email.email)
        email.contacto = request.POST.get('contactomail', email.contacto)
        email.descripcion = request.POST.get('descripcionmail', email.descripcion)
        email.save()
        cliente = email.cliente_set.first()
        return redirect('cliente_edit', id=cliente.id)
    return render(request, 'ClientesApp/cliente_edit_mailedit.html', {'email': email})

@login_required(login_url='/login/login/')
def cliente_edit_teldel(request, id):
    telefono = get_object_or_404(Cliente.telefonos.through, id=id)
    cliente = telefono.cliente
    telefono.delete()
    return redirect('cliente_edit', id=cliente.id)

@login_required(login_url='/login/login/')
def cliente_edit_maildel(request, id):
    email = get_object_or_404(Cliente.emails.through, id=id)
    cliente = email.cliente
    email.delete()
    return redirect('cliente_edit', id=cliente.id)

