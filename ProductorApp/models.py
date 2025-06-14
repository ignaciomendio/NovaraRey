from django.db import models
from ClientesApp.models import CondicionIVA
from AseguradoraApp.models import Cia

# Create your models here.
class Productor(models.Model):
    nombre = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    condicion_iva = models.CharField(max_length=2, choices=CondicionIVA.choices, default=CondicionIVA.MONOTRIBUTO)
    matricula = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - Matricula: {self.matricula}"
    
class CodigoProductor(models.Model):
    productor = models.ForeignKey(Productor, on_delete=models.CASCADE, related_name='codigos_productor')
    codigo = models.CharField(max_length=20, unique=True)
    aseguradora = models.ForeignKey(Cia, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Código: {self.codigo} - Productor: {self.productor.nombre} - Aseguradora: {self.aseguradora.nombre}"
    
    class Meta:
        verbose_name = "Código de Productor"
        verbose_name_plural = "Códigos de Productores"