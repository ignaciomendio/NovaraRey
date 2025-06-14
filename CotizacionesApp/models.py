from django.db import models
from RubrosApp.models import Categoria
from ClientesApp.models import Cliente
from AseguradoraApp.models import Cia

DATA_CHOICES = (    
    ('T', 'Texto'),
    ('N', '´Número'),
    ('B', 'Booleano'),
    ('C', 'Choice'),)

class DataCotizacion(models.Model):
    rubro = models.ForeignKey(Categoria, on_delete=models.CASCADE, verbose_name="Rubro")
    nombre_dato=models.CharField(max_length=50, verbose_name="Nombre del dato")
    tipo_dato=models.CharField(max_length=1, choices=DATA_CHOICES)
    mandatorio = models.BooleanField()
    choices = models.CharField(max_length=150, null=True, blank=True)
    help_text = models.CharField(max_length=250, null=True, blank=True)

class QuotRequest(models.Model):

    QUOT_STATUS_CHOICES = [
        ('P', 'Pendiente'),
        ('F', 'Cotizada'),
        ('C', 'Cancelada'),
    ]

    rubro = models.ForeignKey(Categoria, on_delete=models.CASCADE, verbose_name="Rubro")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    data_cliente = models.CharField(max_length=200, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    usuario_creacion = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, verbose_name='Usuario Creador',related_name='cotizaciones_creadas'
    )
    status = models.CharField(
        max_length=1,
        choices=QUOT_STATUS_CHOICES,
        default='P',
        verbose_name='Estado'
    )
    detalle = models.TextField(verbose_name='Detalle a cotizar')
    usuario_finalizacion = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario de Finalización', related_name='cotizaciones_finalizadas'
    )
    fecha_finalizacion = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Finalización')
    notas_finalización = models.CharField(max_length=250, null=True, blank=True)
    
class Cotizacion(models.Model):

    COTIZACION_STATUS_CHOICES = [
        ('P', 'En Preparación'),
        ('E', 'Enviada al cliente'),
        ('S', 'Solicitada Emisión'),
        ('C', 'Cancelada'),
    ]

    rubro = models.ForeignKey(Categoria, on_delete=models.CASCADE, verbose_name="Rubro")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    data_cliente = models.CharField(max_length=200, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    solicitud_cotizacion = models.ForeignKey(QuotRequest,on_delete=models.CASCADE, verbose_name="Solicitud de Cotizacion", null=True, blank=True)
    sujeto = models.TextField(verbose_name='Detalle a cotizar')
    usuario_creacion = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, verbose_name='Usuario Creador',related_name='nuevas_cotizaciones'
    )
    
    status = models.CharField(
        max_length=1,
        choices=COTIZACION_STATUS_CHOICES,
        default='P',
        verbose_name='Estado'
    )
    
    fecha_envio= models.DateTimeField(verbose_name='Fecha de envio al cliente', null=True, blank=True)
    usuario_envio= models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, verbose_name='Usuario envio',related_name='cotizaciones_enviadas',
        null=True, blank=True
    )
    detalles_envio = models.TextField(verbose_name='Notas de envio', null=True, blank=True)
    
    fecha_sol_emision=models.DateTimeField(verbose_name='Fecha de solicitud emisión', null=True, blank=True)
    usuario_sol_emision= models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, verbose_name='Usuario solicitud de emision',related_name='solicitud_emision',
        null=True, blank=True
    )
    detalles_sol_emision = models.TextField(verbose_name='Notas de solicitud de emision', null=True, blank=True)
    
    usuario_cancelacion = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario de Finalización', related_name='cancela_cotizacion'
    )
    fecha_cancelacion = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Cancelacion')
    notas_cancelacion = models.TextField(verbose_name='Notas de cancelacion de cotizacion', null=True, blank=True)

class CotizacionCia(models.Model):
    cotizacion = models.ForeignKey(Cotizacion,on_delete=models.CASCADE, verbose_name="cotización")
    aseguradora = models.ForeignKey(Cia, on_delete=models.CASCADE, verbose_name="Compañia Aseguradora")
    fecha = models.DateField(verbose_name="Fechas de cotización")
    premio = models.FloatField(verbose_name="Premio en pesos")
    numero = models.CharField(max_length=20, null=True, blank=True)