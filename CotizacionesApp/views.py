from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest
from RubrosApp.models import Categoria
from .models import DataCotizacion, QuotRequest, Cotizacion, CotizacionCia
from ClientesApp.models import Cliente, ClientePersonaFisica, ClientePersonaJuridica
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from AseguradoraApp.models import Cia
from django.utils import timezone
import json

#Vistas para solicitudes de cotización

@login_required(login_url='/login/login/')
def vista_crear_solicitud(req:HttpRequest):
    if req.method == 'POST':
        rubroid = req.POST.get('rubro')
        rubro = get_object_or_404(Categoria, id=rubroid)
        data_cotizacion = DataCotizacion.objects.filter(rubro_id=rubroid)
        clientid = req.POST.get('cliente')
        if clientid:
            cliente_nuevo = False
        else:
            cliente_nuevo = True
        return render(req, 'CotizacionesApp/solicita_cot.html',{"rubro": rubro, "data_cotizacion":data_cotizacion, 
                                                                "cliente_nuevo": cliente_nuevo, "clientid":clientid})
    
    categorias = Categoria.objects.all()
    client_list = []
    for pf in ClientePersonaFisica.objects.all():
        client_list.append((pf.id, f"{pf.apellido}, {pf.nombre}"))
    for pj in ClientePersonaJuridica.objects.all():
        client_list.append((pj.id, pj.razon_social))    
    client_list.sort(key=lambda x: x[1].lower())
    return render(req, 'CotizacionesApp/solicita_cot_fil.html',{"categorias": categorias, "client_list": client_list})

@login_required(login_url='/login/login/')
def vista_ver_solicitudes(req:HttpRequest):

    filtro_status = req.GET.get('status', '').strip()
    filtro_nombre = req.GET.get('nombre', '').strip()

    queryset = QuotRequest.objects.all()

    if filtro_status:
        queryset = queryset.filter(status=filtro_status)

    if filtro_nombre:
        queryset = queryset.filter(
            Q(data_cliente__icontains=filtro_nombre) |
            Q(cliente__clientepersonafisica__nombre__icontains=filtro_nombre) |
            Q(cliente__clientepersonafisica__apellido__icontains=filtro_nombre) |
            Q(cliente__clientepersonajuridica__razon_social__icontains=filtro_nombre)
        )

    return render(req,'CotizacionesApp/solicitudes.html',
                  {"solicitudes": queryset,
                   "filtro_status":filtro_status,
                   "filtro_nombre":filtro_nombre})

@login_required(login_url='/login/login/')
def vista_solicitar(req:HttpRequest):
    if req.method=='POST':
        rubroid = req.POST.get('rubroid')
        categoria = get_object_or_404(Categoria, id=rubroid)
        if req.POST.get('nombre'):
            clt_json = {}
            clt_json["Nombre"]=req.POST.get('nombre')
            clt_json["Tel"]=req.POST.get('telefono')
            clt_json["email"]=req.POST.get('email')

            cliente_contacto = json.dumps(clt_json, ensure_ascii=False)
            cliente = None
        else:
            cliente_contacto = ""
            cliente = get_object_or_404(Cliente, id=req.POST.get('clientid'))
        
        #Carga la data de los controles dinamicos
        data_json = {}
        i = 0
        while True:
            label = req.POST.get(f"label{i}")
            value = req.POST.get(f"data{i}")
            if label is None:
                break  # Ya no hay más datos
            data_json[label] = value
            i += 1

        json_str = json.dumps(data_json, ensure_ascii=False)
        
        
        QuotRequest.objects.create(
            rubro = categoria,
            cliente = cliente,
            data_cliente = cliente_contacto,
            usuario_creacion = req.user,
            detalle = json_str,
            extradata = req.POST.get('extradata'))
        
        messages.success(req, "¡Solicitud creada exitosamente!")
        return redirect('/staff/cotizaciones/solicitudes/?status=P')
    return redirect('/staff/cotizaciones/solicitudes/?status=P')

@login_required(login_url='/login/login/')
def vista_edit_solicitud(req:HttpRequest, id):
    if req.method=='POST':
        solicitud = get_object_or_404(QuotRequest, id=id)
        if solicitud.status != "P":
            messages.error(req, "Solo se pueden editar solicitudes en estado Pendiente.")
            return redirect('/staff/cotizaciones/solicitudes/?status=P')
        solicitud.extradata = req.POST.get('data_detalle')
        solicitud.save()
        messages.success(req, "Solicitud editada correctamente.")
        return redirect('/staff/cotizaciones/solicitudes/?status=P')
    return redirect('/staff/cotizaciones/solicitudes/?status=P')

@login_required(login_url='/login/login/')
def vista_cancel_solicitud(req:HttpRequest, id):
    solicitud = get_object_or_404(QuotRequest, id=id)
    if solicitud.status != "P":
        messages.error(req, "Solo se pueden cancelar solicitudes en estado Pendiente.")
        return redirect('/staff/cotizaciones/solicitudes/?status=P')
    solicitud.status = "C"
    solicitud.usuario_finalizacion = req.user
    solicitud.fecha_finalizacion = timezone.now()
    solicitud.save()
    messages.success(req, "Solicitud cancelada correctamente.")
    return redirect('/staff/cotizaciones/solicitudes/?status=P')

@login_required(login_url='/login/login/')
def vista_cotizar_solicitud(req:HttpRequest, id):
    solicitud = get_object_or_404(QuotRequest, id=id)
    if solicitud.status == "P":
        Cotizacion.objects.create(
            rubro = solicitud.rubro,
            cliente = solicitud.cliente,
            data_cliente = solicitud.data_cliente,
            solicitud_cotizacion = solicitud,
            usuario_creacion = req.user,
            status='P')
        solicitud.status = "F"
        solicitud.usuario_finalizacion = req.user
        solicitud.notas_finalización = "Se generó Cotización"
        solicitud.save()
        messages.success(req, "Cotizacion Creada Correctamente.")
        return redirect('/staff/cotizaciones/listado/?status=P')
    messages.error(req, "Solo se pueden generar cotizaciones de solicitudes Peendientes.")
    return redirect('/staff/cotizaciones/solicitudes/?status=P')

#Vistas para cotizaciones

@login_required(login_url='/login/login/')
def vista_ver_cotizaciones(req:HttpRequest):

    filtro_status = req.GET.get('status', '').strip()
    filtro_nombre = req.GET.get('nombre', '').strip()

    queryset = Cotizacion.objects.all()

    if filtro_status:
        queryset = queryset.filter(status=filtro_status)

    if filtro_nombre:
        queryset = queryset.filter(
            Q(data_cliente__icontains=filtro_nombre) |
            Q(cliente__clientepersonafisica__nombre__icontains=filtro_nombre) |
            Q(cliente__clientepersonafisica__apellido__icontains=filtro_nombre) |
            Q(cliente__clientepersonajuridica__razon_social__icontains=filtro_nombre)
        )

    return render(req,'CotizacionesApp/cotizaciones.html',
                  {"cotizaciones": queryset,
                   "filtro_status":filtro_status,
                   "filtro_choices":Cotizacion.COTIZACION_STATUS_CHOICES,
                   "filtro_nombre":filtro_nombre})

@login_required(login_url='/login/login/')
def vista_cancel_cotizacion(req:HttpRequest, id):
    solicitud = get_object_or_404(Cotizacion, id=id)
    if solicitud.status in ("C", "S"):
        messages.error(req, "Solo se pueden cancelar cotizaciones en prparacion o enviadas a Clientes")
        return redirect('ver_cotizaciones')
    solicitud.status = "C"
    solicitud.usuario_cancelacion = req.user
    solicitud.fecha_cancelacion = timezone.now()
    solicitud.notas_cancelacion = req.POST.get("notas_cancelacion")
    solicitud.save()
    messages.success(req, "Cotización cancelada correctamente.")
    return redirect('/staff/cotizaciones/listado/?status=P')

@login_required(login_url='/login/login/')
def vista_editar_cotizacion(req:HttpRequest, id):
    cotizacion = get_object_or_404(Cotizacion, id=id)
    if cotizacion.status != "P":
        messages.error(req, "La cotización debe estar en preparación para poder editarla")
        return redirect('ver_cotizaciones')       
    if req.method == 'POST':
        cotizacion.extradata = req.POST.get("detalle")
        id_cte = req.POST.get("cliente")
        if id_cte:
            cotizacion.cliente = get_object_or_404(Cliente, id=req.POST.get("cliente"))
        cotizacion.save()
        messages.success(req, "Cotización modificada correctamente.")
        return redirect('/staff/cotizaciones/listado/?status=P')

    filtro_choices = Cotizacion.COTIZACION_STATUS_CHOICES
    cotizaciones_cia = CotizacionCia.objects.filter(cotizacion_id=id)
    companias = Cia.objects.all()
    client_list = []
    for pf in ClientePersonaFisica.objects.all():
        client_list.append((pf.id, f"{pf.apellido}, {pf.nombre}"))
    for pj in ClientePersonaJuridica.objects.all():
        client_list.append((pj.id, pj.razon_social))    
    client_list.sort(key=lambda x: x[1].lower())
    return render(req,'CotizacionesApp/cotizaciones_edit.html',{
        'cotizacion':cotizacion,
        'filtro_choices':filtro_choices,
        'cotizaciones_cia':cotizaciones_cia,
        'companias':companias,
        'client_list': client_list
    })

@login_required(login_url='/login/login/')
def vista_edit_cot_cia(req:HttpRequest, id):
    cot_cia=get_object_or_404(CotizacionCia, id=id)
    if req.method=="POST":
        print(cot_cia)
        idcot = req.POST.get('cotid')
        cot_cia.premio = req.POST.get('premio_edit').replace(',', '.') #convierte formato
        cot_cia.numero = req.POST.get('codigo_edit')
        cot_cia.cobertura = req.POST.get('cobertura_edit')
        cot_cia.save()
        return redirect('editar_cotizacion', id=idcot)
    return redirect('editar_cotizacion', id=idcot)

@login_required(login_url='/login/login/')
def vista_del_cot_cia(req:HttpRequest, idcot, idcot_cia):
    cot_cia=get_object_or_404(CotizacionCia, id=idcot_cia)
    cot_cia.delete()
    return redirect('editar_cotizacion', id=idcot)

@login_required(login_url='/login/login/')
def vista_add_cot_cia(req:HttpRequest):
    idcot = req.POST.get('cotizacionid')
    if req.method=="POST":
        CotizacionCia.objects.create(
            cotizacion = get_object_or_404(Cotizacion, id=idcot),
            aseguradora = get_object_or_404(Cia,id=req.POST.get('cia')),
            fecha = timezone.now(),
            premio = req.POST.get('premio'),
            numero = req.POST.get('codigo'),
            cobertura = req.POST.get('cobertura')
        )
        return redirect('editar_cotizacion', id=idcot)
    return redirect('editar_cotizacion', id=idcot)

    path('cot_cias/add/', vista_add_cot_cia, name='add_cotizacion_cia')


@login_required(login_url='/login/login/')
def vista_send_cotizacion(req:HttpRequest, id):
    solicitud = get_object_or_404(Cotizacion, id=id)
    if solicitud.status != "P":
        messages.error(req, "Solo de úede enviar al cliente Cotizaciones en status EN PREPARACION")
        return redirect('/staff/cotizaciones/listado/?status=P')
    solicitud.status = "E"
    solicitud.usuario_envio = req.user
    solicitud.fecha_envio = timezone.now()
    solicitud.detalles_envio = req.POST.get("notas_envio")
    solicitud.save()
    messages.success(req, "Cotización marcada correctamente como ENVIADA AL CLIENTE.")
    return redirect('/staff/cotizaciones/listado/?status=P')


@login_required(login_url='/login/login/')
def vista_emit_cotizacion(req:HttpRequest, id):
    pass


@login_required(login_url='/login/login/')
def vista_backtop(req:HttpRequest, id):
    solicitud = get_object_or_404(Cotizacion, id=id)
    if solicitud.status != "E":
        messages.error(req, "Solo se puede enviar a Preparacion a cotizaciones ENVIADAS")
        return redirect('/staff/cotizaciones/listado/?status=E')
    solicitud.status = "P"
    solicitud.usuario_envio = None
    solicitud.fecha_envio = None
    solicitud.detalles_envio = ""
    solicitud.save()
    messages.success(req, "Cotización reenviada al status EN PREPARACION")
    return redirect('/staff/cotizaciones/listado/?status=P')
