from django.db import models

# Create your models here.
from django.db import models

class MaterialQuirurgico(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=100)
    stock = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(max_length=50)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    lote = models.CharField(max_length=100, blank=True)
    proveedor = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        app_label = 'insumos_medicos'
        verbose_name = "Material Quirúrgico"
        verbose_name_plural = "Materiales Quirúrgicos"

    def __str__(self):
        return f"{self.nombre} - Stock: {self.stock} {self.unidad_medida}"

class MedicamentoQuirurgico(models.Model):
    nombre = models.CharField(max_length=200)
    principio_activo = models.CharField(max_length=200)
    concentracion = models.CharField(max_length=100)
    presentacion = models.CharField(max_length=100)
    via_administracion = models.CharField(max_length=100)
    stock = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(max_length=50)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    lote = models.CharField(max_length=100, blank=True)
    laboratorio = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        app_label = 'insumos_medicos'
        verbose_name = "Medicamento Quirúrgico"
        verbose_name_plural = "Medicamentos Quirúrgicos"

    def __str__(self):
        return f"{self.nombre} {self.concentracion} - {self.presentacion}"

class UsoMaterial(models.Model):
    operacion = models.ForeignKey('operaciones.Operacion', on_delete=models.CASCADE)
    material = models.ForeignKey(MaterialQuirurgico, on_delete=models.CASCADE)
    cantidad_usada = models.IntegerField()
    fecha_uso = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.material.nombre} - {self.operacion}"

class UsoMedicamento(models.Model):
    operacion = models.ForeignKey('operaciones.Operacion', on_delete=models.CASCADE)
    medicamento = models.ForeignKey(MedicamentoQuirurgico, on_delete=models.CASCADE)
    dosis_aplicada = models.CharField(max_length=50)
    fecha_aplicacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicamento.nombre} - {self.operacion}"
