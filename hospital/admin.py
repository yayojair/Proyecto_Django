from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Doctor)
admin.site.register(Medicamento)
admin.site.register(Sintoma)
admin.site.register(Paciente)
admin.site.register(Consulta)
