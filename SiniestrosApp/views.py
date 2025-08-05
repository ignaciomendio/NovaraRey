from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, FileResponse, Http404
from django.contrib.auth.decorators import login_required
from EmisionesApp.models import Poliza
from .models import Siniestro, DocSiniestro, Tercero
from django.utils import timezone

@login_required(login_url='/login/login/')
def vista_nuevo_siniestro(req: HttpRequest, id: int):
    poliza = get_object_or_404(Poliza, id = id)
    if req.method == 'POST':
        siniestro = Siniestro.objects.create(
            status = Siniestro.SiniestroStatus.RELEVAMIENTO,
            poliza = poliza,
            cobertura = req.POST.get("cobertura",""),
            suma_aseg = float(req.POST.get("suma_aseg")) if req.POST.get("suma_aseg") else None,
            porc_franquicia = float(req.POST.get("franquicia_porc")) if req.POST.get("franquicia_porc") else None,
            franquicia_fija = float(req.POST.get("franquicia_fija")) if req.POST.get("franquicia_fija") else None,
            fecha_ocurrencia = req.POST.get("fecha_ocurrencia"),
            lugar = req.POST.get("lugar_ocurrencia"),
            short_desc = req.POST.get("short_desc"),
            descripcion = req.POST.get("desc_ocurrencia"),
            denunciado = (req.POST.get("denunciado") == "on"),
            terc =  req.POST.get("tercero"),
            danios = req.POST.get("danios_propios","")
        )
        return redirect('list_siniestros')
    
    terceros_choices = Siniestro.TercerosOpciones.choices
    return render(req, 'SiniestrosApp/siniestro_add.html',{
        "poliza": poliza,
        "terceros_choices": terceros_choices,
    })

@login_required(login_url='/login/login/')
def vista_list_siniestros(req:HttpRequest):
    # Obtener Filtros de la solicitud
    fil_status = req.GET.get('fil_status', 'ALL').strip()
    fil_nombre = req.GET.get('fil_nombre', '').strip()
    fil_nro_poliza = req.GET.get('fil_nro_poliza', '').strip()
    fil_siniestro = req.GET.get('fil_siniestros', '').strip()

    # Aplicar filtros a la consulta
    siniestros = Siniestro.objects.all()

    # filtro por status
    selected = []
    if fil_status == 'ALL':
        selected = list(siniestros)
    else:
        selected = [siniestro for siniestro in siniestros if siniestro.status == fil_status]

    # filtro por nombre
    if fil_nombre:
        aux_selected = []
        for siniestro in selected:
            if hasattr(siniestro.poliza.rel_emision.Cotizacion.cliente, 'clientepersonafisica'):
                if (fil_nombre.lower() in siniestro.poliza.rel_emision.Cotizacion.cliente.clientepersonafisica.nombre.lower() or
                    fil_nombre.lower() in siniestro.poliza.rel_emision.Cotizacion.cliente.clientepersonafisica.apellido.lower()):
                    aux_selected.append(siniestro)
            else:
                if (fil_nombre.lower() in siniestro.poliza.rel_emision.Cotizacion.cliente.clientepersonajuridica.razon_social.lower()):
                    aux_selected.append(siniestro)
        selected = aux_selected

    # filtro por número de póliza
    if fil_nro_poliza:
        selected = [siniestro for siniestro in selected if fil_nro_poliza in siniestro.poliza.numero]

    # filtro por nro de sinistro
    if fil_siniestro:
        selected = [siniestro for siniestro in selected if fil_siniestro.lower() in siniestro.nro_siniestro.lower()]
    
    return render(req, 'SiniestrosApp/siniestros.html', {
        'siniestros': selected,
        'status_options': Siniestro.SiniestroStatus.choices,
        'filtro_status_siniestro': fil_status,
        'filtro_nombre': fil_nombre,
        'filtro_nro_poliza': fil_nro_poliza,
        'filtro_siniestro': fil_siniestro,
    })


@login_required(login_url='/login/login/')
def vista_add_note(req: HttpRequest, id: int):
    siniestro = get_object_or_404(Siniestro, id=id)
    if req.method == "POST":
        if siniestro.notas:
            siniestro.notas += f'\n{req.user} - {timezone.now().strftime("%d/%m/%Y")}: {req.POST.get("nueva_nota")}'
        else:
            siniestro.notas = f'{req.user} - {timezone.now().strftime("%d/%m/%Y")}: {req.POST.get("nueva_nota")}'
        siniestro.save()
        return redirect('list_siniestros')
    return redirect('list_siniestros')

@login_required(login_url='/login/login/')
def vista_edit_siniestro(req: HttpRequest, id: int):
    siniestro = get_object_or_404(Siniestro, id=id)
    docs_siniestro = DocSiniestro.objects.filter(siniestro=siniestro)
    terceros = Tercero.objects.filter(siniestro=siniestro)

    if req.method == "POST":
        siniestro.fecha_ocurrencia = req.POST.get("fecha_ocurrencia")
        siniestro.cobertura = req.POST.get("cobertura", "")
        print("suma asegurada: ", float(req.POST.get("suma_aseg")))
        siniestro.suma_aseg = float(req.POST.get("suma_aseg")) if req.POST.get("suma_aseg") else None
        siniestro.porc_franquicia = float(req.POST.get("franquicia_porc")) if req.POST.get("franquicia_porc") else None
        siniestro.franquicia_fija = float(req.POST.get("franquicia_fija")) if req.POST.get("franquicia_fija") else None
        siniestro.lugar = req.POST.get("lugar_ocurrencia")
        siniestro.descripcion = req.POST.get("desc_ocurrencia")
        siniestro.short_desc = req.POST.get("short_desc")
        siniestro.denunciado = req.POST.get("denunciado") == "on"
        siniestro.danios = req.POST.get("danios_propios","")
        siniestro.terc =  req.POST.get("tercero")
        siniestro.nro_siniestro = req.POST.get('info_nro')
        siniestro.liquidador_nombre = req.POST.get('info_liq_nombre','')
        siniestro.liquidador_tel = req.POST.get('info_liq_tel','')
        siniestro.liquidador_mail = req.POST.get('info_liq_mail','')
        fecha_str = req.POST.get('info_inspec_fecha', '')
        if fecha_str:
            siniestro.inspec_fecha = req.POST.get('info_inspec_fecha')
        siniestro.inspec_lugar = req.POST.get('info_inspec_lugar','')
        siniestro.taller = req.POST.get('info_taller','')
        siniestro.save()
        return redirect('list_siniestros')

    return render(req,'SiniestrosApp/siniestro_edit.html',{
        'siniestro': siniestro,
        'terceros_choices': Siniestro.TercerosOpciones.choices,
        'docs_siniestro': docs_siniestro,
        'terceros': terceros
        })

@login_required(login_url='/login/login/')
def vista_add_tercero(req: HttpRequest, id: int):
    siniestro = get_object_or_404(Siniestro, id=id)
    if req.method == "POST":
        Tercero.objects.create(
            siniestro = siniestro,
            nombre = req.POST.get('add_terc_nombre'),
            dni = req.POST.get('add_terc_dni',''),
            tel = req.POST.get('add_terc_tel',''),
            mail = req.POST.get('add_terc_mail',''),
            nro_poliza = req.POST.get('add_terc_poliza',''),
            compania = req.POST.get('add_terc_cia',''),
            bien_afectado = req.POST.get('add_terc_bien',''),
            danios = req.POST.get('add_terc_danios','')
        )
        return redirect('editar_siniestro', siniestro.id)
    return redirect('editar_siniestro', siniestro.id)

@login_required(login_url='/login/login/')
def vista_edit_tercero(req: HttpRequest, id: int):
    siniestro = get_object_or_404(Siniestro, id=id)
    if req.method == "POST":
        terid:int = int(req.POST.get('edit_terc_id'))
        tercero = get_object_or_404(Tercero, id = terid)
        tercero.nombre = req.POST.get('edit_terc_nombre')
        tercero.dni = req.POST.get('edit_terc_dni','')
        tercero.tel = req.POST.get('edit_terc_tel','')
        tercero.mail = req.POST.get('edit_terc_mail','')
        tercero.nro_poliza = req.POST.get('edit_terc_poliza','')
        tercero.compania = req.POST.get('edit_terc_cia','')
        tercero.bien_afectado = req.POST.get('edit_terc_bien','')
        tercero.danios = req.POST.get('edit_terc_danios','')
        tercero.save()
        return redirect('editar_siniestro', siniestro.id)
    return redirect('editar_siniestro', siniestro.id)

@login_required(login_url='/login/login/')
def vista_del_tercero(req: HttpRequest, sinid: int, terid: int):
    tercero = get_object_or_404(Tercero, id = terid)
    tercero.delete()
    return redirect('editar_siniestro', sinid)

@login_required(login_url='/login/login/')
def vista_add_file_siniestro(req:HttpRequest, id):
    siniestro = get_object_or_404(Siniestro, id=id)
    if req.method=='POST':
        print("🧪 FILE:", req.FILES.get("file"))
        DocSiniestro.objects.create(
            usuario_creacion=req.user,
            archivo = req.FILES.get("file"),
            descripcion = req.POST.get("descripcion"),
            siniestro = siniestro,
        )
        return redirect('editar_siniestro', id)
    return redirect('editar_siniestro', id)

@login_required(login_url='/login/login/')
def vista_del_archivo(req: HttpRequest, sinid: int, fileid: int):
    doc = get_object_or_404(DocSiniestro, id = fileid)
    
    doc.archivo.delete(save=False)  # ✅ elimina el archivo físico
    doc.delete()                    # ✅ elimina el registro de la base
    return redirect('editar_siniestro', sinid)

@login_required(login_url='/login/login/')
def vista_add_voucher(req:HttpRequest, id):
    siniestro = get_object_or_404(Siniestro, id=id)
    if req.method == 'POST':
        siniestro.fecha_voucher = timezone.now()
        nro_voucher = req.POST.get('nro_voucher','')
        if nro_voucher:
            siniestro.nro_voucher=nro_voucher
        archivo = req.FILES.get("voucher_file")
        if archivo:
            DocSiniestro.objects.create(
                usuario_creacion=req.user,
                archivo = archivo,
                descripcion = 'Voucher de cierre del siniestro',
                siniestro = siniestro)
        notas_voucher = req.POST.get("voucher_nota",'')
        if notas_voucher:
            if siniestro.notas:
                siniestro.notas += f'\nRESUELTO VIA VOUCHER por {req.user} el {timezone.now().strftime("%d/%m/%Y")}. Notas de cierre: {notas_voucher}'
            else:
                siniestro.notas = f'\nRESUELTO VIA VOUCHER por {req.user} el {timezone.now().strftime("%d/%m/%Y")}. Notas de cierre: {notas_voucher}'
        siniestro.status = Siniestro.SiniestroStatus.VOUCHER
        siniestro.save()
        return redirect('list_siniestros')
    return redirect('list_siniestros')


@login_required(login_url='/login/login/')
def vista_informar_sin(req:HttpRequest, id):
    siniestro = get_object_or_404(Siniestro, id=id)
    if req.method == 'POST':
        siniestro.fecha_informe = timezone.now()
        siniestro.nro_siniestro = req.POST.get('info_nro')
        siniestro.liquidador_nombre = req.POST.get('info_liq_nombre','')
        siniestro.liquidador_tel = req.POST.get('info_liq_tel','')
        siniestro.liquidador_mail = req.POST.get('info_liq_mail','')
        fecha_str = req.POST.get('info_inspec_fecha', '')
        if fecha_str:
            siniestro.inspec_fecha = req.POST.get('info_inspec_fecha')
        siniestro.inspec_lugar = req.POST.get('info_inspec_lugar','')
        siniestro.taller = req.POST.get('info_taller','')
        siniestro.status = Siniestro.SiniestroStatus.INFORMADO
        if siniestro.notas:
            siniestro.notas += f'\nINFORMADO A LA COMPAÑIA por {req.user} el {timezone.now().strftime("%d/%m/%Y")}.'
        else:
            siniestro.notas = f'\nINFORMADO A LA COMPAÑIA por {req.user} el {timezone.now().strftime("%d/%m/%Y")}.'
        siniestro.save()
        return redirect('list_siniestros')
    return redirect('list_siniestros')

@login_required(login_url='/login/login/')
def vista_resolver_sin(req:HttpRequest, id):
    siniestro = get_object_or_404(Siniestro, id=id)
    if req.method == 'POST':
        siniestro.fecha_resolucion = timezone.now()
        siniestro.status = Siniestro.SiniestroStatus.RESUELTO
        mensaje = f'\nMARCADO COMO RESUELTO por {req.user} el {timezone.now().strftime("%d/%m/%Y")}.'
        nota = req.POST.get('resolver_nota','')
        if nota:
            mensaje += f' Notas de Cierre: {nota}'
        if siniestro.notas:
            siniestro.notas += mensaje
        else:
            siniestro.notas = mensaje
        siniestro.save()
        return redirect('list_siniestros')
    return redirect('list_siniestros')

@login_required(login_url='/login/login/')
def vista_rechazar_sin(req:HttpRequest, id):
    siniestro = get_object_or_404(Siniestro, id=id)
    if req.method == 'POST':
        siniestro.fecha_resolucion = timezone.now()
        siniestro.status = Siniestro.SiniestroStatus.RECHAZADO
        mensaje = f'\nMARCADO COMO RECHAZADO por {req.user} el {timezone.now().strftime("%d/%m/%Y")}.'
        nota = req.POST.get('rechazar_nota','')
        if nota:
            mensaje += f' Notas de Cierre: {nota}'
        if siniestro.notas:
            siniestro.notas += mensaje
        else:
            siniestro.notas = mensaje
        siniestro.save()
        return redirect('list_siniestros')
    return redirect('list_siniestros')