from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, FileResponse, Http404
from CotizacionesApp.models import Cotizacion, DataEmision, CotizacionCia
from ClientesApp.models import MedioPago
from .models import Emision, DocEmision, Poliza, Endoso
import json
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
import os
from ProductorApp.models import CodigoProductor
from RubrosApp.models import Categoria
from ContadoApp.models import Pago, PlanPagos
from datetime import datetime


@login_required(login_url='/login/login/')
def vista_new_emision(req: HttpRequest, id: int):
    cotizacion:Cotizacion = get_object_or_404(Cotizacion, id=id)
    if req.method=="POST":
        cotid = req.POST.get("cotid")
        cot_cia:CotizacionCia = get_object_or_404(CotizacionCia, id = cotid)
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

        emision = Emision.objects.create(
            usuario_creacion = req.user,
            Cotizacion = cotizacion,
            cot_cia = cot_cia,
            aceptacion = req.FILES.get("file_aceptacion"),
            extradata = json_str)
        
        cotizacion.status="S"
        cotizacion.fecha_sol_emision=timezone.now()
        cotizacion.usuario_sol_emision= req.user
        cotizacion.save()
        messages.success(req, "Emisión generada correctamente")
        return redirect('editar_emision_completa',emision.id)
    
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

    filtro_poliza = req.GET.get('filtro_poliza','ALL')
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

    return render(req, 'EmisionesApp/emisiones_edit.html', {
        'emision':emision,
        'extradata': extradata,
        'docsEmision':docsEmision,
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
        return redirect(f"{reverse('ver_emisiones')}?filtro_poliza=SP")
    return redirect(f"{reverse('ver_emisiones')}?filtro_poliza=SP")


@login_required(login_url='/login/login/')
def vista_del_file_emision(req, emision_id, file_id):
    emision = get_object_or_404(Emision, id=emision_id)
    archivo = get_object_or_404(DocEmision, id=file_id, emision=emision)

    archivo.archivo.delete(save=False)  # ✅ elimina el archivo físico
    archivo.delete()                    # ✅ elimina el registro de la base

    return redirect(reverse('editar_emision_completa', args=[emision.id]))



@login_required(login_url='/login/login/')
def vista_editar_emision_completa(req:HttpRequest, id):
    emision:Emision = get_object_or_404(Emision, id=id)
    if req.method == "POST":
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
        cotid = req.POST.get("cotid")
        emision.cot_cia = get_object_or_404(CotizacionCia, id=cotid)
        if req.FILES.get("file_aceptacion"):
            if emision.aceptacion:
                archivo_path = emision.aceptacion.path
                if os.path.exists(archivo_path):
                    os.remove(archivo_path)
            emision.aceptacion = req.FILES.get("file_aceptacion")
        emision.save()
        messages.success(req, "Emision Correctamente Modificada")
        return redirect(f"{reverse('ver_emisiones')}?filtro_poliza=SP")

    extradata = emision.dict_extradata()
    docsEmision = DocEmision.objects.filter(emision=emision)
    cotizaciones_cia = CotizacionCia.objects.filter(cotizacion_id=emision.Cotizacion.id)

    return render(req, 'EmisionesApp/edit_emisiones.html', {
        'emision':emision,
        'extradata': extradata,
        'docsEmision':docsEmision,
        "cotizaciones_cia": cotizaciones_cia,
    })

@login_required(login_url='/login/login/')
def vista_cancelar_emision(req:HttpRequest, id):
    emision:Emision = get_object_or_404(Emision, id=id)
    if emision.tiene_poliza:
        messages.error(req, "No se piede cancelar una solictud que ya tiene poliza asignada")
        return redirect(f"{reverse('ver_emisiones')}?filtro_poliza=SP")
    else:
        emision.Cotizacion.status = "E"
        emision.Cotizacion.fecha_sol_emision = None
        emision.Cotizacion.usuario_sol_emision = None
        emision.Cotizacion.detalles_sol_emision = ""
        emision.Cotizacion.save()
        emision.delete()
        messages.success(req, "Emision Cancelada Correctamente")
        return redirect(f"{reverse('ver_emisiones')}?filtro_poliza=SP")

@login_required(login_url='/login/login/')
def vista_add_poliza(req:HttpRequest, id): #el id es el Nro de emision
    emision:Emision = get_object_or_404(Emision, id=id)
    cod_prod = CodigoProductor.objects.filter(aseguradora=emision.cot_cia.aseguradora)
    medios_pago = [
        mp for mp in MedioPago.objects.filter(Cliente=emision.Cotizacion.cliente)
        if not (hasattr(mp, 'tarjetacredito') and mp.tarjetacredito.vencida())]
    #Busca si hay una poliza renovable con la misma emision
    poliza_previa = Poliza.objects.filter(
        rel_emision=emision,
        renovable=True
    ).first()
    if req.method == "POST":
        mp = req.POST.get("pf_mp_in")
        if mp == "CONTADO":
            medio_pago = None
            venc = req.POST.get("pol_venc1_in")
            cuotas = req.POST.get("pol_cuotas_in")
        else:
            medio_pago = get_object_or_404(MedioPago, id=mp)
            venc = None
            cuotas = None

        
        #Creando la poliza
        new_poliza = Poliza.objects.create(
            numero = req.POST.get("pol_num_in"),
            rel_emision = emision,
            rel_medio_pago = medio_pago,
            rel_cod_prod = get_object_or_404(CodigoProductor, id=req.POST.get("pol_prod_in")),
            refacturacion = req.POST.get("pol_refact_in"),
            vencimiento_cuota1 = datetime.fromisoformat(venc).date(),
            cant_cuotas = cuotas,
            pol_previa = poliza_previa.id if poliza_previa else None)

        #Creando el endoso de alta
        Endoso.objects.create(
            poliza = new_poliza,
            numero = 0,
            usuario_creacion = req.user,
            tipo = "A",
            vigencia_desde = req.POST.get("pol_desde_in"),
            vigencia_hasta = req.POST.get("pol_hasta_in"),
            prima = emision.cot_cia.prima,
            premio = emision.cot_cia.premio,
            motivo = "Alta"
        )

        #Creando el plan de pagos
        if not medio_pago:
            plan_pago = PlanPagos.objects.create(
                poliza = new_poliza,
                cantidad_cuotas = int(cuotas),
                status = PlanPagos.Status.ACTIVO,
            )

            #Creando los pagos
            anio = new_poliza.vencimiento_cuota1.year
            mes = new_poliza.vencimiento_cuota1.month
            dia = new_poliza.vencimiento_cuota1.day
            for i in range(int(cuotas)):
                while True:
                    try:
                        nueva_fecha = datetime(anio, mes, dia)
                        break
                    except ValueError:
                        dia -= 1  # Ajusta el día si es inválido
                Pago.objects.create(
                    plan_pago = plan_pago,
                    cuota = i + 1,
                    vencimiento = nueva_fecha,
                    status = Pago.Status.PENDIENTE,
                )
                mes += 1
                if mes > 12:
                    mes = 1
                    anio += 1   
                dia = new_poliza.vencimiento_cuota1.day  # Mantiene el mismo día del mes

        #cambiando status de la emision
        emision.tiene_poliza = True
        emision.save()

        #Si hay poliza previa la marca como No renovable
        if poliza_previa:
            poliza_previa.renovable = False
            poliza_previa.save()
        
        return redirect(reverse('ver_poliza', args=[new_poliza.id]))

    return render(req, 'EmisionesApp/poliza_add.html',
                  {"emision": emision,
                   "cod_prod": cod_prod,
                   "medios_pago": medios_pago,
                   'PolizaRefacturacion': Poliza.PolizaRefacturacion.choices,
                   'poliza_previa': poliza_previa,})

@login_required(login_url='/login/login/')
def vista_list_polizas(req:HttpRequest):
    # Obtener Filtros de la solicitud
    fil_status = req.GET.get('fil_status', '').strip()
    fil_nombre = req.GET.get('fil_nombre', '').strip()
    fil_nro_poliza = req.GET.get('fil_nro_poliza', '').strip()
    fil_rubro = req.GET.get('fil_rubro', '0').strip()
    fil_modelo = req.GET.get('fil_modelo', '').strip()
    fil_patente = req.GET.get('fil_patente', '').strip()
    fil_dias_vencimiento = req.GET.get('fil_dias_vencimiento', '').strip()

    # Aplicar filtros a la consulta
    polizas = Poliza.objects.all()

    # filtro por status
    selected = []
    if fil_status == 'V':
        selected = [poliza for poliza in polizas if poliza.vigente() and poliza.get_vigente().vigente()]
    elif fil_status == 'A':
        selected = [poliza for poliza in polizas if not poliza.activa]
    elif fil_status == 'X':
        selected = [poliza for poliza in polizas if poliza.vigente() and not poliza.get_vigente().vigente()]
    else:
        selected = list(polizas)

    # filtro por nombre
    if fil_nombre:
        aux_selected = []
        for poliza in selected:
            if hasattr(poliza.rel_emision.Cotizacion.cliente, 'clientepersonafisica'):
                if (fil_nombre.lower() in poliza.rel_emision.Cotizacion.cliente.clientepersonafisica.nombre.lower() or
                    fil_nombre.lower() in poliza.rel_emision.Cotizacion.cliente.clientepersonafisica.apellido.lower()):
                    aux_selected.append(poliza)
            else:
                if (fil_nombre.lower() in poliza.rel_emision.Cotizacion.cliente.clientepersonajuridica.razon_social.lower()):
                    aux_selected.append(poliza)
        selected = aux_selected

    # filtro por número de póliza
    if fil_nro_poliza:
        selected = [poliza for poliza in selected if fil_nro_poliza in poliza.numero]

    # filtro por rubro
    if int(fil_rubro)>0:
        selected = [poliza for poliza in selected if poliza.rel_emision.Cotizacion.rubro.id == int(fil_rubro)]

    # filtro por modelo
    if fil_modelo:
        selected = [poliza for poliza in selected if fil_modelo.lower() in poliza.rel_emision.Cotizacion.solicitud_cotizacion.str_detalle().lower()]
    
    # filtro por patente
    if fil_patente:
        selected = [poliza for poliza in selected if fil_patente.lower() in poliza.rel_emision.str_extradata().lower()]

    # filtro por días de vencimiento
    if fil_dias_vencimiento.isdigit():
        dias_vencimiento = int(fil_dias_vencimiento)
        aux_selected = []
        for poliza in selected:
            if poliza.vigente() and poliza.get_vigente().vigente():
                endoso = poliza.get_vigente()
                if endoso.dias_vigencia() <= dias_vencimiento:
                    aux_selected.append(poliza)
        selected = aux_selected
  
    return render(req, 'EmisionesApp/polizas.html', {
        'polizas': selected,
        'status_options': Poliza.PolizaStatus.choices,
        'filtro_status_poliza': fil_status,
        'rubros': Categoria.objects.all(),
        'filtro_rubro': int(fil_rubro) if fil_rubro.isdigit() else 0,
        'filtro_nombre': fil_nombre,
        'filtro_nro_poliza': fil_nro_poliza,
        'filtro_modelo': fil_modelo,
        'filtro_patente': fil_patente,
        'filtro_dias_vencimiento': fil_dias_vencimiento,
    })

@login_required(login_url='/login/login/')
def vista_ver_poliza(req:HttpRequest, id):
    poliza = get_object_or_404(Poliza, id=id)
    endosos = Endoso.objects.filter(poliza=poliza).order_by('-numero')
    docs_emision = DocEmision.objects.filter(emision=poliza.rel_emision)
    medios_pago = MedioPago.objects.filter(Cliente=poliza.rel_emision.Cotizacion.cliente)
    plan_pagos = PlanPagos.objects.filter(poliza=poliza)
    return render(req, 'EmisionesApp/poliza_view.html', {
        'poliza': poliza,   
        'endosos': endosos,
        'docs_emision'  : docs_emision,
        'medios_pago':medios_pago,
        'pagos_vencidos': any(plan.pagos_vencidos() for plan in plan_pagos),
    })

@login_required(login_url='/login/login/')
def vista_editar_endoso(req:HttpRequest, id):
    endoso:Endoso = get_object_or_404(Endoso, id=id)
    if req.method == "POST":

        endoso.vigencia_desde = req.POST.get("vigencia_desde")
        endoso.vigencia_hasta = req.POST.get("vigencia_hasta")
        endoso.prima = req.POST.get("prima")
        endoso.premio = req.POST.get("premio")
        endoso.motivo = req.POST.get("motivo")
        endoso.save()
        messages.success(req, "Endoso modificado correctamente")
        return redirect('ver_poliza', endoso.poliza.id)

    return redirect('ver_poliza', endoso.poliza.id)
    
@login_required(login_url='/login/login/')
def vista_del_endoso(req:HttpRequest, id):
    endoso:Endoso = get_object_or_404(Endoso, id=id)
    poliza = endoso.poliza
    if endoso.tipo == Endoso.EndosoTipo.ALTA:
        messages.error(req, "No se puede eliminar un endoso de alta de poliza")
        return redirect('ver_poliza', poliza.id)
    
    endoso.delete()
    messages.success(req, "Endoso eliminado correctamente")
    return redirect('ver_poliza', poliza.id)


@login_required(login_url='/login/login/')
def descargar_archivo(request, id):
    try:
        doc = DocEmision.objects.get(id=id)
        response = FileResponse(doc.archivo.open('rb'), as_attachment=True, filename=doc.archivo.name.split('/')[-1])
        return response
    except DocEmision.DoesNotExist:
        raise Http404("Archivo no encontrado")

@login_required(login_url='/login/login/')
def vista_endoso_modificacion(req:HttpRequest, id):
    poliza:Poliza = get_object_or_404(poliza, id=id)
    tipo = "Modificación"
    if req.method == "POST":
        pass
    return render(req, 'EmisionesApp/endoso_add.html', {
        'poliza': poliza,
        'tipo': tipo,
    })

@login_required(login_url='/login/login/')
def vista_no_renovar_poliza(req:HttpRequest, id):
    poliza:Poliza = get_object_or_404(Poliza, id=id)
    if req.method == "POST":
        poliza.renovable = False
        poliza.save()
        messages.success(req, "Poliza marcada como no renovable")
        return redirect('ver_poliza', poliza.id)
    
    return redirect('ver_poliza', poliza.id)

@login_required(login_url='/login/login/')
def vista_anular_poliza(req:HttpRequest, id):
    poliza:Poliza = get_object_or_404(Poliza, id=id)
    if req.method == "POST":
        Endoso.objects.create(
            poliza=poliza,
            numero=poliza.cant_endosos + 1,
            usuario_creacion=req.user,
            tipo=Endoso.EndosoTipo.BAJA,
            vigencia_desde=req.POST.get("anula_vigencia_desde"),
            vigencia_hasta=req.POST.get("anula_vigencia_hasta"),
            prima=poliza.get_prima(),
            premio=poliza.get_premio(),
            motivo=req.POST.get("anula_motivo", "Anulación de Póliza")
        )
        poliza.cant_endosos += 1
        poliza.activa = False
        poliza.renovable = False
        poliza.save()
        planes_pago_actuales = PlanPagos.objects.filter(poliza=poliza)
        if planes_pago_actuales.exists():
            planes_pago_actuales.cancelar()
        messages.success(req, "Poliza anulada correctamente")
        return redirect('ver_poliza', poliza.id)
    
    return redirect('ver_poliza', poliza.id)

@login_required(login_url='/login/login/')
def vista_reactivar_poliza(req:HttpRequest, id):
    poliza:Poliza = get_object_or_404(Poliza, id=id)
    if req.method == "POST":
        Endoso.objects.create(
            poliza=poliza,
            numero=poliza.cant_endosos + 1,
            usuario_creacion=req.user,
            tipo=Endoso.EndosoTipo.REHABILITACION,
            vigencia_desde=req.POST.get("reac_vigencia_desde"),
            vigencia_hasta=req.POST.get("reac_vigencia_hasta"),
            prima=req.POST.get("reac_prima"),
            premio=req.POST.get("reac_premio"),
            motivo=req.POST.get("reac_motivo", f"Reactivación de Póliza por {req.user} el {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        )
        poliza.cant_endosos += 1
        poliza.activa = True
        poliza.renovable = True
        poliza.save()
        #si hay planes de pagos cancelados, reactiva el último plan de pagos
        ultimo_plan = PlanPagos.objects.filter(poliza=poliza, status= PlanPagos.Status.ANULADO).last()
        if ultimo_plan.exists():
            ultimo_plan.reactivar()

        messages.success(req, "Poliza rehabilitada correctamente")
        return redirect('ver_poliza', poliza.id)
    
    return redirect('ver_poliza', poliza.id)

@login_required(login_url='/login/login/')
def vista_modificar_conducto(req:HttpRequest, id):
    poliza = get_object_or_404(Poliza, id=id)
    if req.method == "POST":
        Endoso.objects.create(
            poliza=poliza,
            numero=poliza.cant_endosos + 1,
            usuario_creacion=req.user,
            tipo=Endoso.EndosoTipo.MODIFICACION,
            vigencia_desde=poliza.get_vigente().vigencia_desde,
            vigencia_hasta=poliza.get_vigente().vigencia_hasta,
            prima=poliza.get_prima(),
            premio=poliza.get_premio(),
            motivo= "Modificación de Conducto\n" + req.POST.get("mod_conducto_motivo", "")
        )

        mp = req.POST.get("mod_conducto_id")
        if mp == "CONTADO":
            medio_pago = None
            venc =  req.POST.get("mod_venc1_in")
            cuotas = req.POST.get("mod_cuotas_in")
        else:
            medio_pago = get_object_or_404(MedioPago, id=mp)
            venc = None
            cuotas = None

        #Modificando la poliza
        poliza.rel_medio_pago = medio_pago
        poliza.vencimiento_cuota1 = datetime.fromisoformat(venc).date()
        poliza.cant_cuotas = cuotas
        poliza.cant_endosos += 1
        poliza.save()

        #verificando si la poliza ya tiene un plan de pagos activo, si está activo cancela todos los pagos pendientes
        #y cambia el estado del plan a cancelado
        planes_pago_actuales = PlanPagos.objects.filter(poliza=poliza)
        if planes_pago_actuales.exists():
            for plan in planes_pago_actuales:
                plan.cancelar()


        #Creando el nuevo plan de pagos
        if not medio_pago:
            plan_pago = PlanPagos.objects.create(
                poliza = poliza,
                cantidad_cuotas = int(cuotas),
                status = PlanPagos.Status.ACTIVO,
            )

            #Creando los pagos
            anio = poliza.vencimiento_cuota1.year
            mes = poliza.vencimiento_cuota1.month
            dia = poliza.vencimiento_cuota1.day
            for i in range(int(cuotas)):
                while True:
                    try:
                        nueva_fecha = datetime(anio, mes, dia)
                        break
                    except ValueError:
                        dia -= 1  # Ajusta el día si es inválido
                Pago.objects.create(
                    plan_pago = plan_pago,
                    cuota = i + 1,
                    vencimiento = nueva_fecha,
                    status = Pago.Status.PENDIENTE,
                )
                mes += 1
                if mes > 12:
                    mes = 1
                    anio += 1   
                dia = poliza.vencimiento_cuota1.day  # Mantiene el mismo día del mes


        messages.success(req, "Endoso de modificación de conducto cargado correctamente")
        return redirect('ver_poliza', poliza.id)
    return redirect('ver_poliza', poliza.id)

@login_required(login_url='/login/login/')
def vista_modificar_poliza(req:HttpRequest, id):
    poliza:Poliza = get_object_or_404(Poliza, id=id)
    if req.method == "POST":
        Endoso.objects.create(
            poliza=poliza,
            numero=poliza.cant_endosos + 1,
            usuario_creacion=req.user,
            tipo=Endoso.EndosoTipo.MODIFICACION,
            vigencia_desde=req.POST.get("mod_vigencia_desde"),
            vigencia_hasta=req.POST.get("mod_vigencia_hasta"),
            prima=req.POST.get("mod_prima"),
            premio=req.POST.get("mod_premio"),
            motivo=req.POST.get("mod_motivo", "Modificación de Póliza")
        )
        poliza.cant_endosos += 1
        poliza.save()
        messages.success(req, "Endoso de modificación cargado  correctamente")
        return redirect('ver_poliza', poliza.id)
    
    return redirect('ver_poliza', poliza.id)

@login_required(login_url='/login/login/')
def vista_add_observacion_emision(req:HttpRequest, id):
    emision:Emision = get_object_or_404(Emision, id=id)
    if req.method == "POST":
        obs = req.POST.get("obs").strip()
        new_obs = f"{req.user} - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} - {obs}"
        if emision.observaciones:
            emision.observaciones += f"\n{new_obs}" 
        else: 
            emision.observaciones = new_obs
        emision.save()
        messages.success(req, "Observación agregada correctamente")
        return redirect('editar_emision_completa', emision.id)
    
    return redirect(f"{reverse('ver_emisiones')}?filtro_poliza=SP")