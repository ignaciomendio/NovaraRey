from django.db import models
from EmisionesApp.models import Poliza
from django.utils import timezone


class PlanPagos(models.Model):

    class Status(models.TextChoices):
        ACTIVO = 'A', 'Activo'
        CANCELADO = 'C', 'Cancelado'
        FINALIZADO = 'F', 'Finalizado'

    cantidad_cuotas = models.IntegerField(verbose_name="Cantidad de cuotas")
    poliza = models.ForeignKey(Poliza, on_delete=models.CASCADE, verbose_name="Póliza", related_name="plan_pagos")
    creado = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.ACTIVO, verbose_name="Estado")

    def pagos_vencidos(self) -> bool:
        # Devuelve si hay pagos vencidos en el plan
        return any(pago.vencido() for pago in Pago.objects.filter(plan_pago=self, status=Pago.Status.PENDIENTE))
    
    def cancelar(self)-> None:
        # Cancela el plan de pagos
        pagos_plan = Pago.objects.filter(plan_pago=self)
        for pago in pagos_plan:
            if pago.status == Pago.Status.PENDIENTE:
                pago.status = Pago.Status.ANULADO
                pago.observaciones += "\nPlan de pagos cancelado."
                pago.save()
        self.status = self.Status.CANCELADO
        self.save()

    def reactivar(self) -> None:
        # Reactiva el plan de pagos
        pagos_plan = Pago.objects.filter(plan_pago=self, status=Pago.Status.ANULADO)
        if pagos_plan:
            for pago in pagos_plan:
                pago.status = Pago.Status.PENDIENTE
                pago.observaciones += "\nPlan de pagos reactivado."
                pago.save()
            self.status = self.Status.ACTIVO
            self.save()

class Pago(models.Model):

    class Status(models.TextChoices):
        PENDIENTE = 'P', 'Pendiente'
        PAGADO = 'G', 'Pagado'
        ANULADO = 'A', 'Anulado'

    plan_pago = models.ForeignKey(PlanPagos, on_delete=models.CASCADE, verbose_name="Plan de pagos", related_name="pagos")
    cuota = models.IntegerField(verbose_name="Nro de cuota")
    vencimiento = models.DateField(verbose_name="Fecha de vencimiento")
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.PENDIENTE, verbose_name="Estado")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")

    def vencido(self) -> bool:
        # Devuelve si el pago está vencido
        return self.vencimiento < timezone.now().date() and self.status == self.Status.PENDIENTE
    
    def get_status_label(self) -> str:
        # Devuelve la etiqueta del estado del pago
        return self.Status(self.status).label
    
    def es_ultimo_pago(self) -> bool:
        # Devuelve si es el último pago del plan
        return self.cuota == self.plan_pago.cantidad_cuotas

    def str_cuota(self) -> str:
        # Devuelve el número de cuota como string
        return f"{self.cuota} de {self.plan_pago.cantidad_cuotas}"
    
    #metodo para verificar si algun pago aterior aun está pendiente
    def tiene_pagos_pendientes_anteriores(self) -> bool:
        # Verifica si hay pagos pendientes anteriores a este pago
        pagos_anteriores = Pago.objects.filter(plan_pago=self.plan_pago, cuota__lt=self.cuota, status=Pago.Status.PENDIENTE)
        return pagos_anteriores.exists()
    
    #devuelve la cantidad de dias hasta el vencimiento
    def dias_hasta_vencimiento(self) -> int:
        # Calcula la cantidad de días hasta el vencimiento del pago
        return (self.vencimiento - timezone.now().date()).days