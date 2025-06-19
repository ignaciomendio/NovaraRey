from django.shortcuts import render, redirect, get_object_or_404
from RubrosApp.models import Categoria
from django.http import HttpResponse, HttpRequest
from StaffApp.models import Tarea    
from django.contrib.auth.models import User
from datetime import timedelta, datetime
from CotizacionesApp.models import DataCotizacion, QuotRequest
import json


# Create your views here.

def sumar_dias_habiles(fecha, dias):
    contador = 0
    resultado = fecha
    while contador < dias:
        resultado += timedelta(days=1)
        if resultado.weekday() < 5:  # 0=lunes, 4=viernes
            contador += 1
    return resultado

def vista_rubros(request:HttpRequest)->HttpResponse:
    rubros = Categoria.objects.all()
    return render(request, 'RubrosApp/rubros.html',{"rubros": rubros})

def more_info(request:HttpRequest)->HttpResponse:

    
    if request.method == 'POST':
        rubro_id = request.POST.get('rubroId')
        rubro = Categoria.objects.get(id=rubro_id)
        cliente = request.POST.get('nombreCliente')
        metodo = request.POST.get('metodoContacto')
        whatsapp = request.POST.get('whatsappCliente')
        mail = request.POST.get('emailCliente')
        mensaje = "Enviar a " + cliente + " por " + metodo + " a " 
        if metodo == "whatsapp":
            mensaje += whatsapp
        elif metodo == "email":
            mensaje += mail
        mensaje += " informacion adicional sobre seguros de " + rubro.nombre
        Tarea.objects.create(
            titulo=mensaje,
            usuario_creacion=User.objects.get(username="auto"),
            fecha_vencimiento=sumar_dias_habiles(datetime.now(), 3),
            status='P',
            notas="",
            usuario_finalizacion=None
        )
        mensaje_exito = "¡Gracias por tu interés " + cliente + "! En breve nos estaremos contactando para hacerle llegar la información solicitada."
        rubros = Categoria.objects.all()
        return render(request, 'RubrosApp/rubros.html', {'rubros': rubros, 'mensaje_exito': mensaje_exito})
    else:
        return HttpResponse("Invalid request method.", status=405)
    
def vista_solicitar_cotizacion(req:HttpRequest, id):
    categoria = get_object_or_404(Categoria, id=id)
    if req.method=="POST":
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

        clt_json = {}
        clt_json["Nombre"]=req.POST.get('nombre')
        clt_json["Tel"]=req.POST.get('telefono')
        clt_json["email"]=req.POST.get('email')

        json_cte = json.dumps(clt_json, ensure_ascii=False)

        QuotRequest.objects.create(
            rubro = categoria,
            data_cliente = json_cte,
            usuario_creacion = User.objects.get(username="auto"),
            detalle = json_str,
            extradata = req.POST.get('rawdata'))
        mensaje_exito = "¡Gracias por tu solicitud! En breve nuestro equipo se estrá comunicando con la cotización solicitada o para profundizar sobre los detalles de sus necesidades."
        rubros = Categoria.objects.all()
        return render(req, 'RubrosApp/rubros.html', {'rubros': rubros, 'mensaje_exito': mensaje_exito})
    data_cotizacion = DataCotizacion.objects.filter(rubro_id=id)
    return render(req, 'RubrosApp/solicita_cot.html',{"data_cotizacion": data_cotizacion, "categoria": categoria.nombre})