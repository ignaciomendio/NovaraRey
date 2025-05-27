from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib.auth.models import User
from django.utils import timezone

@login_required(login_url='/login/login/')
def vista_dashboard(request):
    """
    Render the dashboard view.
    """
    return render(request, 'StaffApp/dashboard.html')

@login_required(login_url='/login/login/')
def vista_enter(request):
    if request.user.is_authenticated:
        # If the user is authenticated, redirect to the dashboard
        return render(request, 'StaffApp/dashboard.html')
    else:
        return redirect('login')
    
@login_required(login_url='/login/login/')
def vista_tareas_main(request):
    tareas = Tarea.objects.filter(status='P').order_by('fecha_vencimiento')
    return render(request, 'StaffApp/tareasMain.html', {'tareas': tareas})


@login_required(login_url='/login/login/')
def vista_tareas_create(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        fecha_vencimiento = request.POST.get('fecha_vencimiento')
        status = 'P'
        
        tarea = Tarea(
            titulo=titulo,
            usuario_creacion=request.user,
            fecha_vencimiento=fecha_vencimiento,
            status=status,
        )
        tarea.save()
        return redirect('tareas_main')
    
    return render(request, 'StaffApp/tareasCreate.html')


@login_required(login_url='/login/login/')
def vista_tareas_edit(request, id): 
    tarea = Tarea.objects.get(id=id)
    
    if request.method == 'POST':

        accion = request.POST.get('accion')
        if accion == 'addcomment':
            comentario = request.POST.get('comentario')
            if comentario:
                usuario = request.user.username
                timestamp = timezone.localtime(timezone.now()).strftime('%d/%m/%Y %H:%M')
                tarea.notas += f"\n[{usuario}:{timestamp}]: {comentario}"
                tarea.save()
                return redirect('tareas_main')
            else:
                # If no comment is provided, redirect to the edit view
                return redirect('tareas_edit', id=id)

        elif accion == 'finalizar':
            tarea.status = 'F'
            tarea.usuario_finalizacion = request.user
            tarea.fecha_finalizacion = timezone.now()
            tarea.save()
            return redirect('tareas_main')

        elif accion == 'cancelar':
            tarea.status = 'C'
            tarea.usuario_finalizacion = request.user
            tarea.fecha_finalizacion = timezone.now()
            tarea.save()
            return redirect('tareas_main')
            
    return render(request, 'StaffApp/tareasEdit.html', {'tarea': tarea})


@login_required(login_url='/login/login/')
def vista_tareas_export(request):
    from django.http import HttpResponse
    import pandas as pd

    # Obtén todos los campos de Tarea como diccionarios
    tareas = Tarea.objects.all().values('id', 'titulo', 'notas', 'status', 'fecha_creacion', 'fecha_vencimiento',
    'usuario_creacion__username', 'usuario_finalizacion__username', 'fecha_finalizacion')

    for tarea in tareas:
        tarea['fecha_creacion'] = tarea['fecha_creacion'].replace(tzinfo=None)
        tarea['fecha_vencimiento'] = tarea['fecha_vencimiento'].replace(tzinfo=None)
        if tarea['fecha_finalizacion']:
            tarea['fecha_finalizacion'] = tarea['fecha_finalizacion'].replace(tzinfo=None)

    df = pd.DataFrame(list(tareas))
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="tareas.xlsx"'
    
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Tareas')

    return response

@login_required(login_url='/login/login/')
def vista_prestadores_main(request):
    rubrofilter = request.GET.get('rubrofilter', None)
    activofilter = request.GET.get('activofilter', None)
    nombrefilter = request.GET.get('nombrefilter', None)
    prestadores = Prestador.objects.all().order_by('rubro__nombre', 'nombre')
    if rubrofilter:
        prestadores = prestadores.filter(rubro__id=rubrofilter)
    if activofilter:
        if activofilter == '1':
            prestadores = prestadores.filter(activo=True)
        elif activofilter == '0':
            prestadores = prestadores.filter(activo=False)
    if nombrefilter:
        prestadores = prestadores.filter(nombre__icontains=nombrefilter)
    rubros = RubroPrestador.objects.all().order_by('nombre')
    
    return render(request, 'StaffApp/prestadoresMain.html', {'prestadores': prestadores, 'rubros': rubros})
    
@login_required(login_url='/login/login/')
def vista_prestadores_sendmail(request):
    if request.method == 'POST':
        prestador_id = request.POST.get('prestador_id')
        prestador = Prestador.objects.get(id=prestador_id)
        
        # Aquí puedes implementar la lógica para enviar el correo electrónico
        # Por ejemplo, usando send_mail de django.core.mail
        
        return redirect('prestadores_main')
    
    return render(request, 'StaffApp/prestadoresSendMail.html')

@login_required(login_url='/login/login/')
def vista_prestadores_create(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        rubro_id = request.POST.get('rubro')
        contacto = request.POST.get('contacto')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        direccion = request.POST.get('direccion')
        sitio_web = request.POST.get('sitio_web')
        observaciones = request.POST.get('observaciones')
        activo = True

        rubro = RubroPrestador.objects.get(id=rubro_id)
        
        prestador = Prestador(
            nombre=nombre,
            rubro=rubro,
            contacto=contacto,
            telefono=telefono,
            email=email,    
            direccion=direccion,
            sitio_web=sitio_web,
            observaciones=observaciones,
            activo = True
        )
        prestador.save()
        return redirect('prestadores_main')
    
    rubros = RubroPrestador.objects.all().order_by('nombre')
    return render(request, 'StaffApp/prestadoresCreate.html', {'rubros': rubros})

@login_required(login_url='/login/login/')
def vista_prestadores_edit(request, id):
    prestador = Prestador.objects.get(id=id)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        rubro_id = request.POST.get('rubro')
        direccion = request.POST.get('direccion')
        sitio_web = request.POST.get('sitio_web')
        observaciones = request.POST.get('observaciones')

        rubro = RubroPrestador.objects.get(id=rubro_id)
        
        prestador.nombre = nombre
        prestador.rubro = rubro
        prestador.direccion = direccion
        prestador.sitio_web = sitio_web
        prestador.observaciones = observaciones
        prestador.save()
        
        return redirect('prestadores_main')
    
    rubros = RubroPrestador.objects.all().order_by('nombre')
    return render(request, 'StaffApp/prestadoresEdit.html', {'prestador': prestador, 'rubros': rubros})