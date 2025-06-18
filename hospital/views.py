from django.shortcuts import render, redirect, get_object_or_404
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
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime


def es_doctor(user):
    """
    Verifica si el usuario pertenece al grupo 'Doctores'.
    Este método se utiliza como filtro de acceso para limitar ciertas vistas únicamente a usuarios que
    forman parte del grupo 'Doctores', definido en el sistema de autenticación de Django.

    Parámetros:
    ----------
    user : User
        Objeto de usuario autenticado que realiza la solicitud.

    Retorna:
    -------
    bool
        True si el usuario pertenece al grupo 'Doctores', False en caso contrario.
    """
    return user.groups.filter(name='doctores').exists()


def login_doctor(request):
    """
    Vista encargada de gestionar el inicio de sesión para usuarios con rol de doctor.
    Si el usuario ya se encuentra autenticado, se le redirige a la página principal ('home').
    En caso de recibir una solicitud POST, se validan las credenciales ingresadas. Si son correctas
    y el usuario pertenece al grupo 'Doctores', se inicia sesión y se redirige a la página principal.
    En cualquier otro caso, se recarga el formulario con un indicador de error.

    Parámetros:
    ----------
    request : HttpRequest
        Objeto que representa la solicitud HTTP recibida por el servidor.

    Retorna:
    -------
    HttpResponse
        Página de inicio ('home') si el inicio de sesión es exitoso.
        Página de login ('login.html') con un mensaje de error si la autenticación falla.
    """
    error = ''

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        nombre = request.POST.get('uname')
        psw = request.POST.get('psw')
        user = authenticate(username=nombre, password=psw)

        if user is not None and user.is_active:
            if es_doctor(user):
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Acceso restringido a usuarios con rol de doctor.")
                #error = "Acceso restringido a usuarios con rol de doctor."
        else:
            messages.error(request, "Credenciales inválidas. Intente nuevamente.")
            #error = "Credenciales inválidas. Intente nuevamente."

    #return render(request, 'login.html', {'error': error})
    return render(request, "login.html")


@user_passes_test(es_doctor, login_url='login')
def index(request):
    """
    Vista protegida que muestra la página principal para usuarios del grupo 'Doctores'.
    Esta vista solo está disponible para usuarios autenticados que pertenezcan al grupo 'Doctores'.

    Parámetros:
    ----------
    request : HttpRequest
        Objeto que representa la solicitud HTTP recibida.

    Retorna:
    -------
    HttpResponse
        Renderiza la plantilla 'index.html' si el usuario pertenece al grupo correspondiente.
    """
    doctor = Doctor.objects.get(user=request.user)
    nombre_doctor = doctor.nombre + " " +doctor.apellido
    return render(request, 'index.html', {'nombre_doctor': nombre_doctor or request.user.username})


def validar_datos_paciente(post_data):
    """
    Valida los datos ingresados en el formulario de registro de paciente.
    Esta función asegura que todos los campos obligatorios estén presentes y que la edad tenga un valor válido.

    Parámetros:
    ----------
    post_data : QueryDict
        Diccionario con los datos enviados en la solicitud POST.

    Retorna:
    -------
    int
        Edad validada y convertida a entero.
    """
    campos_obligatorios = ['nombre', 'apellidos', 'edad', 'sintomas', 'medicamentos', 'peso']
    for campo in campos_obligatorios:
        if not post_data.get(campo):
            raise ValueError("Todos los campos son obligatorios")

    try:
        edad = int(post_data.get('edad'))
        if edad < 0 or edad > 120:
            raise ValueError("La edad debe ser mayor a 0 y menor a 120")
    except ValueError:
        raise ValueError("La edad debe ser un número válido")

    return edad


def crear_paciente(data, doctor):
    """
    Crea un nuevo paciente en la base de datos y lo asocia al doctor correspondiente.

    Parámetros:
    ----------
    data : dict
        Diccionario con los datos del paciente (nombre, apellidos, edad, sexo).

    doctor : Doctor
        Instancia del modelo Doctor asociada al usuario autenticado.

    Retorna:
    -------
    Paciente
        Objeto Paciente creado y guardado.
    """
    paciente = Paciente(
        nombre=data['nombre'],
        apellido=data['apellidos'],
        edad=data['edad'],
        sexo=data['genero'],
        estado='activo'
    )
    paciente.save()

    # Asociación del paciente con el doctor que realiza el registro
    paciente.doctor.add(doctor)

    return paciente


def crear_consulta(data, paciente, doctor):
    """
    Registra una nueva consulta médica asociada al paciente y al doctor.
    Además, agrega los síntomas y medicamentos especificados en el formulario.

    Parámetros:
    ----------
    data : dict
        Diccionario con los datos de la consulta (observaciones, peso, fecha, síntomas, medicamentos).

    paciente : Paciente
        Instancia del paciente al que se le realiza la consulta.

    doctor : Doctor
        Instancia del doctor que realiza la consulta.

    Retorna:
    -------
    Consulta
        Objeto Consulta creado y guardado.
    """
    consulta = Consulta(
        observacion=data.get('observaciones'),
        peso=data.get('peso'),
        fecha=parse_datetime(data.get('fecha')),
        paciente=paciente,
        doctor=doctor
    )
    consulta.save()

    # Asociación de síntomas (separados por coma)
    sintomas = [s.strip() for s in data.get('sintomas', '').split(',') if s.strip()]
    consulta.sintoma.add(*Sintoma.objects.filter(nombre__in=sintomas))

    # Asociación de medicamentos (separados por coma)
    medicamentos = [m.strip() for m in data.get('medicamentos', '').split(',') if m.strip()]
    consulta.medicamento.add(*Medicamento.objects.filter(nombre__in=medicamentos))

    return consulta

@login_required(login_url='login')
def registro_paciente(request):
    """
    Vista protegida que permite registrar un nuevo paciente y su consulta médica.
    Esta función valida los datos del formulario, crea un paciente, lo asocia con el médico autenticado
    y registra una consulta con los síntomas y medicamentos indicados.

    Parámetros:
    ----------
    request : HttpRequest
        Solicitud HTTP enviada por el navegador del usuario.

    Retorna:
    -------
    HttpResponse
        - Si la solicitud POST se completa correctamente, redirige a la misma página con un mensaje de éxito.
        - Si hay errores de validación o ejecución, renderiza el formulario con mensajes de error.
    """
    if request.method == 'POST':
        try:
            # Validar los datos del formulario
            edad = validar_datos_paciente(request.POST)

            # Obtener al doctor asociado al usuario autenticado
            doctor = Doctor.objects.get(user=request.user)

            # Preparar los datos para crear paciente y consulta
            data = request.POST.copy()
            data['edad'] = edad  # incluir edad convertida a int

            # Crear y guardar paciente
            paciente = crear_paciente(data, doctor)

            # Crear y guardar consulta asociada
            crear_consulta(data, paciente, doctor)

            messages.success(request, "Se registró con éxito el paciente")
            return redirect("registro-paciente")

        except ValueError as ve:
            messages.error(request, str(ve))
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")

    return render(request, 'registroPaciente.html')

@login_required(login_url='login') #permitir solo ver a usuario registrados
def listar_pacientes(request):
    """
    Vista que permite visualizar el listado de pacientes activos.
    Esta función consulta todos los registros de pacientes cuyo estado sea 'activo' 
    y los pasa a la plantilla para su visualización. Además, serializa la lista de 
    pacientes en formato JSON para ser utilizada, por ejemplo, en scripts JavaScript 
    dentro del HTML.

    Parámetros:
    ----------
    request : HttpRequest
        Objeto que representa la solicitud HTTP realizada por el usuario autenticado.

    Retorna:
    -------
    HttpResponse
        Renderiza la plantilla 'listarPacientes.html', incluyendo en el contexto:
            - 'pacientes': queryset con los pacientes activos.
            - 'pacientes_json': datos serializados en formato JSON del mismo queryset.
    """
    # Consulta todos los pacientes con estado 'activo'
    pacientes = Paciente.objects.filter(estado = 'activo')
    pacientes_json = serializers.serialize('json', pacientes)
    return render(request, 'listarPacientes.html', {"pacientes_json": pacientes_json, "pacientes":pacientes})

def actualizar_paciente(request):
    """
    Vista que permite actualizar los datos básicos de un paciente a través de una solicitud HTTP POST con datos JSON.
    Esta función espera un cuerpo de solicitud en formato JSON que contenga el identificador del paciente (`idpaciente`)
    y los campos a modificar. Solo los campos definidos como permitidos serán actualizados. Si la operación es exitosa,
    retorna una respuesta JSON con estado de éxito; en caso contrario, devuelve un mensaje de error correspondiente.

    Parámetros:
    ----------
    request : HttpRequest
        Objeto que representa la solicitud HTTP, la cual debe ser de tipo POST y contener un cuerpo JSON.

    Retorna:
    -------
    JsonResponse
        - 200 OK: si la actualización se realiza correctamente.
        - 400 Bad Request: si faltan datos, el JSON es inválido o no hay campos válidos para actualizar.
        - 404 Not Found: si el paciente con el ID proporcionado no existe.
        - 405 Method Not Allowed: si la solicitud no es de tipo POST.
        - 500 Internal Server Error: para cualquier otro error inesperado.
    """
    if request.method == 'POST':
        try:
            # Intenta convertir el cuerpo de la solicitud a un diccionario desde JSON
            datos = json.loads(request.body)
            id_paciente = datos.get('idpaciente')
            
            if not id_paciente:
                return JsonResponse({"error": "ID de paciente requerido"}, status=400)
            # Busca al paciente por su clave primaria  
            paciente = Paciente.objects.get(pk=id_paciente)
            
            # Lista de campos permitidos para actualizar
            campos_permitidos = ['nombre', 'apellido', 'edad']
            
            actualizaciones = 0
            for clave, valor in datos.items():
                if clave in campos_permitidos:
                    setattr(paciente, clave, valor)
                    actualizaciones += 1
            
            if actualizaciones == 0:
                return JsonResponse({"error": "No se proporcionaron campos válidos para actualizar"}, status=400)
            
            # Guarda los cambios en la base de datos
            paciente.save()
            return JsonResponse({"success": True, "message": "Paciente actualizado correctamente"})
            
        except Paciente.DoesNotExist:
            return JsonResponse({"error": "Paciente no encontrado"}, status=404)
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Datos JSON inválidos"}, status=400)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    # Si se intenta acceder con otro método
    return JsonResponse({"error": "Método no permitido"}, status=405)

def eliminacion_logica_paciente(request):
    """
    Vista que permite marcar como inactivo (eliminar lógicamente) a un paciente mediante una solicitud POST en formato JSON.
    Esta función no elimina el registro físicamente de la base de datos, sino que actualiza el campo `estado` del paciente a "inactivo".
    El objetivo es preservar los datos históricos del paciente, cumpliendo con buenas prácticas de eliminación lógica.

    Parámetros:
    ----------
    request : HttpRequest
        Solicitud HTTP recibida, la cual debe ser de tipo POST y contener un cuerpo en formato JSON con el ID del paciente.

    Retorna:
    -------
    JsonResponse
        - 200 OK: Si la operación fue exitosa.
        - 400 Bad Request: Si faltan datos o el JSON es inválido.
        - 404 Not Found: Si no se encuentra el paciente con el ID especificado.
        - 405 Method Not Allowed: Si la solicitud no es de tipo POST.
        - 500 Internal Server Error: Para errores no controlados.
    """
    if request.method == 'POST':
        try:
            # Intenta parsear el cuerpo de la solicitud como JSON
            datos = json.loads(request.body)
            id_paciente = datos.get('idpaciente')
            
            if not id_paciente:
                return JsonResponse({"error": "ID de paciente requerido"}, status=400)
            
            # Busca al paciente por su clave primaria (ID)
            paciente = Paciente.objects.get(pk=id_paciente)
            
            # Realiza eliminación lógica cambiando el estado a 'inactivo'
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

def logout_doctor(request):
    """
    Vista que gestiona el cierre de sesión (logout) para usuarios del sistema administrativo.
    Esta función verifica primero si el usuario está activo. Si no lo está, se le redirige directamente
    a la página de inicio de sesión. Si el usuario está activo, se realiza el cierre de sesión y 
    posteriormente se redirige al login.

    Parámetros:
    ----------
    request : HttpRequest
        Objeto que representa la solicitud HTTP realizada por el usuario.

    Retorna:
    -------
    HttpResponseRedirect
        Redirige al usuario a la página de inicio de sesión ('login') tras cerrar sesión 
        o si no se encuentra activo.
    """
    # Verifica si el usuario está activo (autenticado y con cuenta habilitada)
    if not request.user.is_active:
        return redirect("login")
    
    # Cierra la sesión del usuario actual
    logout(request)

    # Redirige al login tras cerrar sesión
    return redirect('login')

@login_required(login_url='login')
def detalle_paciente(request, paciente_id):
    """
    Vista que muestra el historial de consultas médicas de un paciente específico.
    Esta función recupera al paciente mediante su identificador (`paciente_id`) y obtiene 
    todas las consultas asociadas, ordenadas por fecha descendente (de la más reciente a la más antigua).
    La información se envía al template para su visualización.

    Parámetros:
    ----------
    request : HttpRequest
        Objeto que representa la solicitud HTTP realizada por el usuario.

    paciente_id : int
        Identificador único del paciente cuyo historial se desea consultar.

    Retorna:
    -------
    HttpResponse
        Renderiza la plantilla 'consultas_paciente.html' con los datos del paciente y su historial de consultas.
    """
    # Obtiene el paciente o lanza un error 404 si no existe
    paciente = get_object_or_404(Paciente, pk=paciente_id)

    # Recupera todas las consultas del paciente ordenadas por fecha descendente
    consultas = paciente.consultas.order_by('-fecha')

    # Renderiza la plantilla con los datos del paciente y sus consultas
    return render(request, 'consultas_paciente.html', {'paciente': paciente, 'consultas': consultas})

def nueva_consulta(request, paciente_id):
    """
    Vista que permite registrar una nueva consulta médica para un paciente específico.
    Esta función permite, mediante una solicitud POST, crear una nueva instancia del modelo `Consulta`
    y asociarla a un paciente y al doctor autenticado. También permite vincular los síntomas y medicamentos
    registrados durante dicha consulta.

    Parámetros:
    ----------
    request : HttpRequest
        Objeto que representa la solicitud HTTP realizada por el usuario.

    paciente_id : int
        Identificador único del paciente al que se le registrará la consulta.

    Retorna:
    -------
    HttpResponse
        - Si la solicitud es POST y la creación es exitosa, redirige a la vista 'listar-pacientes' con un mensaje de éxito.
        - Si la solicitud no es POST, renderiza el formulario para registrar la consulta (actualmente apunta a 'listarPacientes.html').

    Excepciones:
    -----------
    - Retorna un error 404 si el paciente con el ID proporcionado no existe.
    - Puede lanzar errores no controlados si los campos esperados no están en el formulario o no tienen el formato correcto.
    """
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    doctor = Doctor.objects.get(user=request.user)
    if request.method == 'POST':
        datos = request.POST.copy()
        crear_consulta(datos, paciente, doctor)
        messages.success(request, "se creo con exito la consulta")
        return redirect("listar-pacientes")
    
    return render(request, 'listarPacientes.html')
