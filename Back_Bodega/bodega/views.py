from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Usuarios
from .serializers import *


@api_view(["GET"])
def Traer_usuarios(request):
    usuarios = Usuarios.objects.all()
    serializer = UsuarioSerializer(usuarios, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def Iniciar_sesion(request):
    usuario_data = request.data
    if not usuario_data.get('rut'):
        return Response({'mensaje': "No Se a ingresado Usuario", 'estado': False})
    if not usuario_data.get('password'):
        return Response({'mensaje': "No Se a ingresado Contraseña", 'estado': False})
    usuario = Usuarios.objects.filter(usu_rut=usuario_data.get('rut')).first()
    if not usuario:
        return Response({'mensaje': "Usuario no válido", 'estado': False})
    serializer = UsuarioSerializer(usuario)
    if usuario.usu_password == usuario_data.get('password'):
        return Response({'mensaje': "Usuario y contraseña válidos", 'estado': True, 'rol': serializer.data['usu_rol']})
    else:
        return Response({'mensaje': "Contraseña no Valida", 'estado': False})
