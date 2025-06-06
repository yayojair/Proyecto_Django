from django.shortcuts import render, redirect
from django.contrib.auth.models import User #usuarios registrados en el sistema
from django.contrib.auth import authenticate, logout, login
#authenticate: verifica si el usuario y contraseña proporcionados son correctos.
#login: inicia la sesión y guarda al usuario en request.user.
#logout: Cierra la sesión del usuario actual
from.models import *
from django.core import serializers
import json
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import user_passes_test
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required



#login
def login_usuarios(request):
    error = ''
    if request.method == 'POST':
        nombre = request.POST['uname']
        psw = request.POST['psw']
        user = authenticate(username=nombre, password=psw)
        if user is not None and user.is_active and user.is_staff:
            login(request, user)
            return redirect('home')
        else:
            error = "si"
    return render(request, 'login.html', {'error': error})

def es_staff(user):
    return user.is_staff

@user_passes_test(es_staff, login_url='login')
def Index(request):
    return render(request, 'index.html')

@login_required(login_url='login')
def registro_paciente(request):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            apellidos = request.POST.get('apellidos')
            edad = request.POST.get('edad')
            genero = request.POST.get('genero')
            sintomas = request.POST.get('sintomas')
            estado = "activo"

            if not nombre or not apellidos or not edad or not sintomas:
                messages.error(request, "Todos los campos son obligatorios")
                return render(request, "registroPaciente.html")
            try:
                edad = int(edad)
                if edad < 0 or edad > 120:
                    messages.error(request, "la edad debe ser mayor a 0 y menor a 120")
                    return render(request, "registroPaciente.html")
            except ValueError:
                messages.error(request, "La edad debe ser un número válido")
                return render(request, 'registroPaciente.html')
            
            paciente = Paciente(nombre = nombre,
                            apellido = apellidos,
                            edad = edad,
                            sexo = genero,
                            sintomas = sintomas,
                            estado = estado)
            paciente.save()

            messages.success(request, "se registro con exito el paciente")
            return redirect("registro-paciente")
        
        except Exception as e:
            # Loggear el error en producción
            messages.error(request, f"Ocurrió un error al registrar el paciente: {str(e)}")

    return render(request, 'registroPaciente.html')

@login_required(login_url='login') #permitir solo ver a usuario registrados
def listar_pacientes(request):
    pacientes = Paciente.objects.filter(estado = 'activo').order_by('-idpaciente')
    pacientes_json = serializers.serialize('json', pacientes)
    return render(request, 'listarPacientes.html', {"pacientes_json": pacientes_json, "pacientes":pacientes})

def actualizar_paciente(request):
    if request.method == 'POST':
        try:
            datos = json.loads(request.body)
            id_paciente = datos.get('idpaciente')
            
            if not id_paciente:
                return JsonResponse({"error": "ID de paciente requerido"}, status=400)
                
            paciente = Paciente.objects.get(pk=id_paciente)
            
            # Lista de campos permitidos para actualizar
            campos_permitidos = ['nombre', 'apellido', 'edad', 'sexo', 'id', 'sintomas']
            
            actualizaciones = 0
            for clave, valor in datos.items():
                if clave in campos_permitidos:
                    setattr(paciente, clave, valor)
                    actualizaciones += 1
            
            if actualizaciones == 0:
                return JsonResponse({"error": "No se proporcionaron campos válidos para actualizar"}, status=400)
            paciente.save()
            return JsonResponse({"success": True, "message": "Paciente actualizado correctamente"})
            
        except Paciente.DoesNotExist:
            return JsonResponse({"error": "Paciente no encontrado"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Datos JSON inválidos"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)       

def elimina_paciente(request):
    if request.method == 'POST':
        try:
            datos = json.loads(request.body)
            id_paciente = datos.get('idpaciente')
            
            if not id_paciente:
                return JsonResponse({"error": "ID de paciente requerido"}, status=400)
                
            paciente = Paciente.objects.get(pk=id_paciente)
            
            paciente.estado = "inactivo"      
            paciente.save()
            return JsonResponse({"success": True, "message": "Paciente eliminado correctamente"})
            
        except Paciente.DoesNotExist:
            return JsonResponse({"error": "Paciente no encontrado"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Datos JSON inválidos"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)

def logout_admin(request):
    if not request.user.is_staff: #verifica si el usuario es un miembro del personal
        return redirect("login")
    logout(request)
    return redirect('login')