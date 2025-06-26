from django.db import models
from django.core.validators import RegexValidator

cp_validator = RegexValidator(
    regex=r'^[A-Z]?\d{4}[A-Z]{0,3}$',
    message='Ingrese un código postal válido'
)

class AdressType(models.Model):
    tipo = models.CharField(max_length=50, verbose_name="Tipo de dirección")
    
    class Meta:
        verbose_name="Tipo de dirección"
        verbose_name_plural="Tipos de dirección"
    
    def __str__(self):
        return self.tipo

class Address(models.Model):
    calle = models.CharField(max_length=50, verbose_name="Calle")
    numero = models.CharField(max_length=10, verbose_name="Número")
    piso = models.CharField(max_length=10, verbose_name="Piso", null=True, blank=True)
    dpto = models.CharField(max_length=10, verbose_name="Dpto", null=True, blank=True)
    localidad = models.CharField(max_length=50, verbose_name="Localidad")
    provincia = models.CharField(max_length=50, verbose_name="Provincia")
    cp = models.CharField(max_length=8, validators=[cp_validator], verbose_name="Código Postal")
    tipo = models.ForeignKey(AdressType, on_delete=models.CASCADE, verbose_name="Tipo de dirección")
    
    class Meta:
        verbose_name="Dirección"
        verbose_name_plural="Direcciones"
    
    def __str__(self):
        return self.calle + " " + self.numero + ", " + self.localidad + ", " + self.provincia
