from django.db import models
from CotizacionesApp.models import Cotizacion, CotizacionCia
from ProductorApp.models import CodigoProductor
from ClientesApp.models import MedioPago, TarjetaCredito, TransferenciaBancaria
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
    cancelada = models.BooleanField(verbose_name="Solicitud Cancelada", default=False)
    fecha_cancelacion = models.DateTimeField(verbose_name='Fecha de cancelacion', null=True, blank=True)
    usuario_cancelación = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, verbose_name='Usuario Cancelador',related_name='cancelar_emisiones',
        null=True, blank=True
    )
    notas_cancelacion = models.TextField(verbose_name="Notas de cancelación", null=True, blank=True)
    observaciones = models.TextField(verbose_name="Observaciones", null=True, blank=True)

    def dict_extradata(self)->dict | None:
        if self.extradata:
            return json.loads(self.extradata)
        else:
            return None
    
    def str_extradata(self)->str:
        dic: dict|None = self.dict_extradata()
        aux_str = ""
        if dic:
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

    class PolizaStatus(models.TextChoices): 
        VIGENTE = 'V', 'Vigente'
        ANULADA = 'A', 'Anulada'
        VENCIDA = 'X', 'Vencida'
        

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    numero = models.CharField(max_length=20, verbose_name="Número de POliza")
    rel_emision = models.ForeignKey(Emision, on_delete=models.CASCADE, verbose_name="Emisión")
    rel_medio_pago =  models.ForeignKey(MedioPago, on_delete=models.SET_NULL, verbose_name="Medio de Pago", null=True, blank=True)
    rel_cod_prod = models.ForeignKey(CodigoProductor, on_delete=models.CASCADE, verbose_name="Código de Productor", default=1)
    refacturacion = models.CharField(max_length=2, choices=PolizaRefacturacion.choices, verbose_name="Período de refacturación")
    activa = models.BooleanField(verbose_name="Poliza Activa", default=True)
    vencimiento_cuota1 = models.DateTimeField(verbose_name="Vencmiento 1er cupón", null=True, blank=True)
    cant_cuotas = models.IntegerField(verbose_name="Cantidad de cuotas", null=True, blank=True)
    pol_previa = models.BigIntegerField(verbose_name="Poliza Previa", null=True, blank=True, default=None)
    cant_endosos = models.IntegerField(verbose_name="Cantidad de endosos", default=0)
    renovable = models.BooleanField(verbose_name="Póliza Renovable", default=True)
  

    def meses_refacturacion(self):
        return REFACTURACION[self.refacturacion]

    def aging_creation(self)->int:
        ahora = timezone.now()
        return (ahora.date() - self.fecha_creacion.date()).days


    def pago_contado(self)->bool:
        return not self.rel_medio_pago
    
    def get_medio_pago(self) -> str:
        if self.pago_contado:
            return "CONTADO"
        else:
            return self.get_tipo_display()

    def get_vigente(self):
        # Devuelve el último endoso vigente
        endosos = Endoso.objects.filter(poliza=self)
        res = None
        for endoso in endosos:
            if endoso.vigente():
                res = endoso
        return res

    def vigente(self)->bool:
        end_vigente = self.get_vigente()
        # si hay un endoso vigente, verificamos que no sea de tipo BAJA
        if end_vigente:
            return end_vigente.tipo != Endoso.EndosoTipo.BAJA
        # si no hay endosos, la póliza no está vigente
        return self.get_vigente() != None

    def get_prima(self)->float:
        # Devuelve la prima del último endoso vigente
        endoso = self.get_vigente()
        if endoso:
            return endoso.prima
        return 0.0  
    
    def get_prima_str(self)->str:
        # Devuelve la prima del último endoso vigente como string con dos decimales
        prima = self.get_prima()
        return f"{prima:.2f}"
    
    def get_premio(self)->float:
        # Devuelve el premio del último endoso vigente
        endoso = self.get_vigente()
        if endoso:
            return endoso.premio
        return 0.0
    
    def get_premio_str(self)->str:
        # Devuelve el premio del último endoso vigente como string con dos decimales
        premio = self.get_premio()
        return f"{premio:.2f}"

    def get_status(self)->str:
        # Devuelve el estado de la póliza
        if self.activa:
            if self.vigente():
                return self.PolizaStatus.VIGENTE.label
            else:
                return self.PolizaStatus.VENCIDA.label
        else:
            return self.PolizaStatus.ANULADA.label

    def get_vigencia_desde(self):
        # Devuelve la fecha de vigencia original de la poliza
        endoso_alta = Endoso.objects.filter(poliza=self, tipo=Endoso.EndosoTipo.ALTA).first()
        if endoso_alta:
            return endoso_alta.vigencia_desde
        return None
    
    def get_vigencia_hasta(self):
        # Devuelve la fecha de vigencia original de la poliza
        endoso_alta = Endoso.objects.filter(poliza=self, tipo=Endoso.EndosoTipo.ALTA).first()
        if endoso_alta:
            return endoso_alta.vigencia_hasta
        return None


class Endoso(models.Model):

    class EndosoTipo(models.TextChoices):
        ALTA = 'A', 'Alta'
        MODIFICACION = 'M', 'Modificación'
        BAJA = 'B', 'Anulación'
        REHABILITACION = 'R', 'Rehabilitacion'

    poliza = models.ForeignKey(Poliza, on_delete=models.CASCADE, verbose_name="Endoso")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    usuario_creacion = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, verbose_name='Usuario Creador',related_name='nueva_poliza'
    )
    numero = models.IntegerField(verbose_name="Número de endoso")
    tipo = models.CharField(max_length=1, choices=EndosoTipo.choices, verbose_name="Tipo de endoso")
    vigencia_desde = models.DateTimeField(verbose_name="Comienzo de vigencia")
    vigencia_hasta = models.DateTimeField(verbose_name="Fin de vigencia")
    prima = models.FloatField(verbose_name="Prima")
    premio = models.FloatField(verbose_name="Prima")
    motivo = models.TextField(verbose_name="Motivo del endoso", null=True, blank=True)

    def vigente(self)->bool:
        ahora = timezone.now()
        return (self.vigencia_hasta >= ahora) 
    
    def dias_vigencia(self)->int:
        ahora = timezone.now()
        return (self.vigencia_hasta.date() - ahora.date()).days

    def get_numero(self)->str:
        return f"{self.poliza.numero}-{self.numero}"



