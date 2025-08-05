from django.db import models
from EmisionesApp.models import Poliza
from django.utils import timezone

class Siniestro(models.Model):

    class SiniestroStatus(models.TextChoices): 
        RELEVAMIENTO = 'P', 'En relevamiento'
        INFORMADO = 'I', 'Informado a Compañía'
        RESUELTO = 'R', 'Resuelto'
        VOUCHER = 'V', 'Resuelto Via Voucher'
        RECHAZADO = 'X', 'Rechazado por la compañía'

    class TercerosOpciones(models.TextChoices):
        SIN_TERCEROS = 'N', 'Sin terceros involucrados'
        RESPONSABLE = 'R', 'Tercero Responsable'
        DAMNIFICADO = 'D' , 'Tercero Damnificado'

    #Datos del siniestro obligatorios que tienen que tenr todos los siniestros
    status = models.CharField(max_length=1, choices=SiniestroStatus, default='P')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    poliza = models.ForeignKey(Poliza, on_delete=models.CASCADE, verbose_name="Póliza")
    fecha_ocurrencia = models.DateTimeField(verbose_name="Fecha y hora de ocurrencia del siniestro")
    lugar = models.CharField(max_length=120, verbose_name="Lugar de ocurrencia del siniestro")
    short_desc = models.CharField(max_length=20, verbose_name="Descripcion corta del sinistro", default="Siniestro")
    descripcion = models.TextField(verbose_name="Descripción del siniestro")
    denunciado = models.BooleanField(verbose_name="Con denuncia pollicial", default=False)
    terc = models.CharField(max_length=1, choices=TercerosOpciones.choices, default='N')
    reclamo_ter = models.BooleanField(verbose_name="Tiene reclamo terceros", default=False)

    #Datos del siniestro que pueden o no estar
    danios = models.TextField(verbose_name="Descripción de los daños propios", null=True, blank=True) 
    cobertura = models.CharField(max_length=50, verbose_name="Tipo de cobertura de la poliza", blank=True, null=True)
    suma_aseg = models.FloatField(verbose_name="Suma asegurada", null=True, blank=True)
    porc_franquicia = models.FloatField(verbose_name="Porcentaje Franquicia", null=True, blank=True)
    franquicia_fija = models.FloatField(verbose_name="Franquicia Fija", blank=True, null=True)
    notas = models.TextField(verbose_name="Notas de seguimiento", null=True, blank=True) 
    causa_no_reclammo = models.CharField(max_length=60, verbose_name="Causa de no generacion de reclamo a terceros", null=True, blank=True)

    #Datos de seguimiento si resuelve con Voucher
    fecha_voucher = models.DateField(verbose_name="Fecha de generación de Voucher", null=True, blank=True)
    nro_voucher = models.CharField(max_length=18, verbose_name="Nro de Voucher", null=True, blank=True)

    #Datos de seguimiento si resuelve con siniestro informado
    fecha_informe = models.DateField(verbose_name="Fecha de informe de siniestro a la cía", null=True, blank=True)
    nro_siniestro = models.CharField(max_length=18, verbose_name="Nro de siniestro", null=True, blank=True)
    liquidador_nombre = models.CharField(max_length=40, verbose_name="Nombre del liquidador", null=True, blank=True)
    liquidador_tel = models.CharField(max_length=20, verbose_name="Teléfono del liquidador", null=True, blank=True)
    liquidador_mail = models.EmailField(verbose_name="E-Mail del liquidador", null=True, blank=True)
    inspec_fecha = models.DateField(verbose_name="Fecha de inspección", null=True, blank=True)
    inspec_lugar = models.CharField(max_length=50, verbose_name="Lugar de la inspección", null=True, blank=True)
    taller = models.CharField(max_length=50, verbose_name="Taller o servicio técnico asignado", null=True, blank=True)
    fecha_resolucion = models.DateField(verbose_name="Fecha de informe de resolución de siniestro", null=True, blank=True)


class Tercero(models.Model):
    siniestro = models.ForeignKey(Siniestro, on_delete=models.CASCADE, verbose_name="Siniestro")
    nombre = models.CharField(max_length=50, verbose_name="Nombre del Tercero")
    dni = models.CharField(max_length=12, verbose_name="DNI del Tercero", null=True, blank=True)
    tel = models.CharField(max_length=20, verbose_name="teléfono del Tercero", null=True, blank=True)
    mail = models.EmailField(max_length=25, verbose_name="mail del Tercero", null=True, blank=True)
    nro_poliza = models.CharField(max_length=12, verbose_name="Número de póliza del Tercero", null=True, blank=True)
    compania = models.CharField(max_length=20, verbose_name="Aseguradora del Tercero", null=True, blank=True)
    bien_afectado = models.CharField(max_length=80, verbose_name="Bien del tercero afectado por el siniestro", blank=True, null=True)
    danios = models.TextField(verbose_name="Descripción de los daños al tercer", null=True, blank=True) 


class DocSiniestro(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    usuario_creacion = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, verbose_name='Usuario Creador',related_name='docs_siniestro_creados'
    )
    archivo = models.FileField(
        upload_to='siniestros/', 
        verbose_name='Archivos asociados a siniestros', 
        null=True, blank=True
    )
    descripcion = models.CharField(max_length=60, verbose_name="Descripción del Archivo")
    siniestro = models.ForeignKey(Siniestro, on_delete=models.CASCADE, verbose_name='Emisión')

    def aging_creation(self)->int:
        if self.fecha_creacion:
            ahora = timezone.now()
            return (ahora.date() - self.fecha_creacion.date()).days
        return 0
    
    def delete(self, *args, **kwargs): #type: ignore
        """Elimina el archivo de Google Drive y luego el registro de base de datos."""
        if self.archivo:
            # El storage personalizado se encarga de eliminar de Google Drive
            self.archivo.delete(save=False)
        super().delete(*args, **kwargs)