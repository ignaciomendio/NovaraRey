from django.db import models
from CotizacionesApp.models import Cotizacion, CotizacionCia
from ProductorApp.models import CodigoProductor
from ClientesApp.models import MedioPago
from AseguradoraApp.models import Cia
from django.utils import timezone
import json

REFACTURACION: dict = {
    "M": 1,
    "BM": 2,
    "TM": 3,
    "CM": 4,
    "SM": 6,
    "A": 12,
}

class Emision(models.Model):

    MAX_DIAS_SIN_POLIZA = 3

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    usuario_creacion = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, verbose_name='Usuario Creador',related_name='nuevas_emisiones'
    )
    Cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, verbose_name='Cotización')
    cot_cia = models.ForeignKey(CotizacionCia, on_delete=models.CASCADE, verbose_name='Cotizacion de la compañia',default=None)
    aceptacion = models.FileField(
        upload_to='aceptaciones/', 
        verbose_name='Archivos de aceptación del Cliente', 
        null=True, blank=True
    )
    extradata = models.TextField(verbose_name="Datos extra", null=True, blank=True)
    tiene_poliza = models.BooleanField(verbose_name="Tiene Poliza", default=False)
    cod_prod = models.ForeignKey(CodigoProductor, on_delete=models.CASCADE, null=True, blank=True)

    def dict_extradata(self)->dict:
        return json.loads(self.extradata)
    
    def str_extradata(self)->str:
        dic: dict = self.dict_extradata()
        aux_str = ""
        for clave, valor in dic.items():
            aux_str += clave + ": " + str(valor) + "\n"
        return aux_str
    
    def aging_creation(self)->int:
        if self.fecha_creacion:
            ahora = timezone.now()
            return (ahora.date() - self.fecha_creacion.date()).days
        return 0
    
    def cotizar_vencida(self)->bool:
        return self.aging_creation() > self.MAX_DIAS_SIN_POLIZA

class DocEmision(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    usuario_creacion = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, verbose_name='Usuario Creador',related_name='nuevo_doc_emision'
    )
    archivo = models.FileField(
        upload_to='filesEmisiones/', 
        verbose_name='Archivos asociados a emisiones', 
        null=True, blank=True
    )
    descripcion = models.CharField(max_length=60, verbose_name="Descripción del Archivo")
    emision = models.ForeignKey(Emision, on_delete=models.CASCADE, verbose_name='Emisión')

    def aging_creation(self)->int:
        if self.fecha_creacion:
            ahora = timezone.now()
            return (ahora.date() - self.fecha_creacion.date()).days
        return 0

class Poliza(models.Model):

    class PolizaRefacturacion(models.TextChoices):
        MENSUAL = 'M', 'Mensual'
        BIMESTRAL = 'BM', 'Bimestral'
        TRIMESTRAL = 'TM', 'Trimestral'
        CUATRIMESTRAL = 'CM', 'Cuatrimestral'
        SEMESTRAL = 'SM', 'Semestral'
        ANUAL = 'A', 'Anual'
        

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    usuario_creacion = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, verbose_name='Usuario Creador',related_name='nueva_poliza'
    )
    numero = models.CharField(max_length=20, verbose_name="Número de POliza")
    rel_emision = models.ForeignKey(Emision, on_delete=models.CASCADE, verbose_name="Emisión")
    rel_medio_pago =  models.ForeignKey(MedioPago, on_delete=models.SET_NULL, verbose_name="Emisión", null=True, blank=True)
    refacturacion = models.CharField(max_length=2, choices=PolizaRefacturacion.choices, verbose_name="Período de refacturación")
    fecha_vencimiento = models.DateTimeField(verbose_name="Fecha de vencimiento")

    def meses_refacturacion(self):
        return REFACTURACION[self.refacturacion]

    def aging_creation(self)->int:
        if self.fecha_creacion:
            ahora = timezone.now()
            return (ahora.date() - self.fecha_creacion.date()).days
        return 0

    def dias_vigencia(self)->int:
        if self.fecha_vencimiento:
            ahora = timezone.now()
            return (self.fecha_vencimiento.date() - ahora.date()).days
        return 0