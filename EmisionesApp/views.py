from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest
from CotizacionesApp.models import Cotizacion, DataEmision, CotizacionCia
from ClientesApp.models import MedioPago
from .models import Emision, DocEmision
import json
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from ProductorApp.models import CodigoProductor 


@login_required(login_url='/login/login/')
def vista_new_emision(req: HttpRequest, id: int):
    cotizacion:Cotizacion = get_object_or_404(Cotizacion, id=id)
    if req.method=="POST":
        cotid = req.POST.get("cotid")
        cot_cia:CotizacionCia = get_object_or_404(CotizacionCia, id = cotid)

        emision = Emision.objects.create(
            usuario_creacion = req.user,
            Cotizacion = cotizacion,
            cot_cia = cot_cia,
            aceptacion = req.FILES.get("file_aceptacion"))
        
        cotizacion.status="S"
        cotizacion.fecha_sol_emision=timezone.now()
        cotizacion.usuario_sol_emision= req.user
        cotizacion.save()
        messages.success(req, "Emisión generada correctamente")
        return redirect('edita_emision',emision.id)
    
    cotizaciones_cia = CotizacionCia.objects.filter(cotizacion_id=id)
    extradata = DataEmision.objects.filter(rubro=cotizacion.rubro)
    return render(req, "EmisionesApp/emisiones_add.html", {
        "cotizacion":cotizacion,
        "cotizaciones_cia":cotizaciones_cia,
        "extradata":extradata})

@login_required(login_url='/login/login/')
def vista_ver_emisiones(req:HttpRequest):

    FILTER_OPTIONS =[
        ("SP", "Sin Poliza"),
        ("CP", "Con Poliza"),
        ("ALL", "Todas")]

    filtro_poliza = req.GET.get('filtro_poliza')
    filtro_nombre = req.GET.get('nombre', '').strip()

    if filtro_poliza=="SP":
        emisiones = Emision.objects.filter(tiene_poliza=False)
    elif filtro_poliza=="CP":
        emisiones = Emision.objects.filter(tiene_poliza=True)
    else:
        emisiones = Emision.objects.all()

    if filtro_nombre:
        emisiones = emisiones.filter(
            Q(Cotizacion__cliente__clientepersonafisica__nombre__icontains=filtro_nombre) |
            Q(Cotizacion__cliente__clientepersonafisica__apellido__icontains=filtro_nombre) |
            Q(Cotizacion__cliente__clientepersonajuridica__razon_social__icontains=filtro_nombre)
        )

    return render(req, 'EmisionesApp/emisiones.html', {
        'emisiones':emisiones,
        'filter_options': FILTER_OPTIONS,
        'filtro_poliza': filtro_poliza,
        'filtro_nombre':filtro_nombre,
    })

@login_required(login_url='/login/login/')
def vista_editar_emision(req:HttpRequest, id):
    emision:Emision = get_object_or_404(Emision, id=id)
    extradata = DataEmision.objects.filter(rubro=emision.Cotizacion.rubro)
    if req.method=="POST":
        prod_code = req.POST.get('prod-cod')
        prod = get_object_or_404(CodigoProductor, id=prod_code)
        if extradata:
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
            emision.extradata = json_str
        emision.cod_prod = prod
        emision.save()
        return redirect('ver_emisiones')

    docsEmision = DocEmision.objects.filter(emision=emision)
    cod_productores = CodigoProductor.objects.filter(aseguradora=emision.cot_cia.aseguradora, activo=True)

    return render(req, 'EmisionesApp/emisiones_edit.html', {
        'emision':emision,
        'extradata': extradata,
        'docsEmision':docsEmision,
        'cod_productores':cod_productores,
    })

@login_required(login_url='/login/login/')
def vista_add_file_emision(req:HttpRequest, id):
    emision = get_object_or_404(Emision, id=id)
    if req.method=='POST':
        DocEmision.objects.create(
            usuario_creacion=req.user,
            archivo = req.FILES.get("file"),
            descripcion = req.POST.get("descripcion"),
            emision = emision,
        )
        print("descrpcion: ", req.POST.get("descripcion"))
        return redirect(reverse('edita_emision',args=[emision.id]))
    return redirect(reverse('edita_emision',args=[emision.id]))


@login_required(login_url='/login/login/')
def vista_del_file_emision(req, emision_id, file_id):
    emision = get_object_or_404(Emision, id=emision_id)
    archivo = get_object_or_404(DocEmision, id=file_id, emision=emision)

    archivo.archivo.delete(save=False)  # ✅ elimina el archivo físico
    archivo.delete()                    # ✅ elimina el registro de la base

    return redirect(reverse('edita_emision', args=[emision.id]))


