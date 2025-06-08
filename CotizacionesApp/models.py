from django.db import models


AUTO_CHOICES = (    ('A', 'Automotor'),
    ('M', 'Moto'),)

class Std_Automotor(models.Model):
    tipo = models.CharField(
        max_length=1,choices=AUTO_CHOICES, default='A', verbose_name="Tipo de Automotor")
    modelo = models.CharField(max_length=80, verbose_name="Modelo")


    class Meta:
        verbose_name = "Automotor"
        verbose_name_plural = "Automotores"
    
    def __str__(self):
        return self.modelo
