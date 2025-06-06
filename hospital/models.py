from django.db import models

class Doctor (models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    edad = models.IntegerField()
    sexo = models.CharField(max_length=7)

    def __str__(self):
        return self.nombre

# Create your models here.
class Paciente(models.Model):
    idpaciente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    edad = models.IntegerField()
    sexo = models.CharField(max_length=7)
    sintomas = models.CharField(max_length=200)
    estado = models.CharField(max_length=9, default='activo')
    #doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    def __str__(self):
        return self.nombre
    
class Citas(models.Model):

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha = models.DateField()
    horario = models.TimeField()
    
    def __str__(self):
        return self.doctor.nombre +" -- "+ self.paciente.nombre
    
