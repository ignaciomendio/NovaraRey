from django.db import models
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User

class RubroPrestador(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre del Rubro')
    descripcion = models.TextField(verbose_name='Descripción', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Rubro de Prestador'
        verbose_name_plural = 'Rubros de Prestadores'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Prestador(models.Model):

    nombre = models.CharField(max_length=100, verbose_name='Nombre del Prestador')
    rubro = models.ForeignKey(RubroPrestador, on_delete=models.CASCADE, verbose_name='Rubro')
    contacto = models.CharField(max_length=100, verbose_name='Nombre de Contacto', blank=True, null=True)
    telefono = models.CharField(max_length=15, verbose_name='Teléfono', blank=True, null=True)
    email = models.EmailField(verbose_name='Email', blank=True, null=True)
    direccion = models.CharField(max_length=255, verbose_name='Dirección', blank=True, null=True)
    sitio_web = models.URLField(verbose_name='Sitio Web', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    observaciones = models.TextField(verbose_name='Observaciones', blank=True, null=True)
   
    
    class Meta:
        verbose_name = 'Prestador'
        verbose_name_plural = 'Prestadores'
        ordering = ['rubro__nombre', 'nombre']


    def __str__(self):
        return self.nombre + ' (' + self.rubro.nombre + ')'
    

class Tarea(models.Model):
    TASK_STATUS_CHOICES = [
        ('P', 'Pendiente'),
        ('F', 'Completada'),
        ('C', 'Cancelada'),
    ]
    titulo = models.CharField(max_length=100, verbose_name='Título')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    usuario_creacion = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='tareas_creadas', verbose_name='Usuario Creador'
    )
    fecha_vencimiento = models.DateTimeField(verbose_name='Fecha de Vencimiento')
    status = models.CharField(
        max_length=1,
        choices=TASK_STATUS_CHOICES,
        default='P',
        verbose_name='Estado'
    )
    notas = models.TextField(verbose_name='Descripción')
    usuario_finalizacion = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='tareas_finalizadas', null=True, blank=True, verbose_name='Usuario de Finalización'
    )
    fecha_finalizacion = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Finalización')


    class Meta:
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.titulo
    
    def dias_restantes(self):
        """
        Calcula los días restantes hasta la fecha de vencimiento.
        """
        if self.fecha_vencimiento:
            hoy = timezone.now().date()
            vencimiento = self.fecha_vencimiento.date()
            return (vencimiento - hoy).days
        return None
