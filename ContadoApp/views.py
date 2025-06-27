from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, FileResponse, Http404
from django.contrib.auth.decorators import login_required
from .models import PlanPagos, Pago
from RubrosApp.models import Categoria
from django.utils import timezone
from django.contrib import messages


@login_required(login_url='/login/login/')
def vista_ver_pagos(req: HttpRequest):
    # Obtener Filtros de la solicitud
    fil_status = req.GET.get('fil_status', '').strip()
    fil_nombre = req.GET.get('fil_nombre', '').strip()
    fil_nro_poliza = req.GET.get('fil_nro_poliza', '').strip()
    fil_rubro = req.GET.get('fil_rubro', '0').strip()

    # Aplicar filtros a la consulta
    pagos = Pago.objects.all()

    # filtro por status
    selected = list(pagos)

    if fil_status:
        if fil_status != 'ALL':
            selected = [pago for pago in selected if pago.status == fil_status]

    print(f"Selected pagos: {len(selected)}")

    # filt por nombre
    if fil_nombre:
        aux_selected = []
        for pago in selected:
            if hasattr(pago.plan_pago.poliza.rel_emision.Cotizacion.cliente, 'clientepersonafisica'):
                if (fil_nombre.lower() in pago.plan_pago.poliza.rel_emision.Cotizacion.cliente.clientepersonafisica.nombre.lower() or
                    fil_nombre.lower() in pago.plan_pago.poliza.rel_emision.Cotizacion.cliente.clientepersonafisica.apellido.lower()):
                    aux_selected.append(pago)
            else:
                if (fil_nombre.lower() in pago.plan_pago.poliza.rel_emision.Cotizacion.cliente.clientepersonajuridica.razon_social.lower()):
                    aux_selected.append(pago)
        selected = aux_selected


    # filtro por número de póliza
    if fil_nro_poliza:
        selected = [pago for pago in selected if fil_nro_poliza in pago.plan_pago.poliza.numero]

    # filtro por rubro
    if int(fil_rubro)>0:
        selected = [pago for pago in selected if pago.plan_pago.poliza.rel_emision.Cotizacion.rubro.id == int(fil_rubro)]

    selected.sort(key=lambda x: x.vencimiento)
  
    return render(req, 'ContadoApp/pagos.html', {
        'cuotas': selected,
        'status_options': Pago.Status.choices,
        'fil_status': fil_status,
        'rubros': Categoria.objects.all(),
        'filtro_rubro': int(fil_rubro) if fil_rubro.isdigit() else 0,
        'filtro_nombre': fil_nombre,
        'filtro_nro_poliza': fil_nro_poliza,
    })

@login_required(login_url='/login/login/')
def vista_add_comment(req: HttpRequest, pk: int):
    pago = get_object_or_404(Pago, pk=pk)

    if req.method == 'POST':
        obs= f"{req.user} - {timezone.now().strftime('%Y-%m-%d %H:%M')} - {req.POST.get('observaciones', '').strip()}"
        if pago.observaciones:
            pago.observaciones += f"\n{obs}"
        else:
            pago.observaciones = obs
        pago.save()
        return redirect('ver_pagos')

    return redirect('ver_pagos')

@login_required(login_url='/login/login/')
def vista_pagar_cuota(req: HttpRequest, pk: int):
    pago = get_object_or_404(Pago, pk=pk)

    if pago.status != Pago.Status.PENDIENTE:
        messages.error(req, "El pago ya ha sido procesado o no está pendiente.")
        return redirect('ver_pagos')
    
    if pago.tiene_pagos_pendientes_anteriores():
        messages.error(req, "No se puede pagar esta cuota porque hay pagos pendientes anteriores.")
        return redirect('ver_pagos')

    pago.status = Pago.Status.PAGADO
    msg = f"{req.user} - {timezone.now().strftime('%Y-%m-%d %H:%M')} - Pago marcado como pagado."
    if pago.observaciones:
        pago.observaciones += f"\n{msg}"
    else:
        pago.observaciones = msg
        
    if pago.es_ultimo_pago():
        pago.plan_pago.status = PlanPagos.Status.FINALIZADO
        pago.plan_pago.save()

    pago.save()
    messages.success(req, "Pago registrado correctamente.")
    return redirect('ver_pagos')

