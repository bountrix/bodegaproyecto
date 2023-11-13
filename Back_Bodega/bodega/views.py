from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from datetime import datetime
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from django.db.models import Case, When, Value


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
        return Response({'mensaje': "Usuario y contraseña válidos", 'estado': True, 'rol': serializer.data['usu_rol'], 'id': serializer.data['usu_id']})
    else:
        return Response({'mensaje': "Contraseña no Valida", 'estado': False})


@api_view(["GET"])
def Traer_Productos(request):
    producto = Productos.objects.values(
        'pro_id', 'pro_nombre', 'pro_marca__mar_nombre', 'pro_stock', 'pro_precio').order_by('pro_id')
    if producto:
        return Response({'estado': True, 'data': producto})
    return Response({'estado': False})


@api_view(["POST"])
def Descontar_Producto(request):
    if request.method == "POST":
        producto_id = request.data.get("producto_id")
        cantidad_a_descontar = request.data.get("cantidad_a_descontar")
        usu_id = request.data.get("usu_id")

        try:
            producto = Productos.objects.get(pro_id=producto_id)
            producto.pro_stock = int(producto.pro_stock)
            cantidad_a_descontar = int(cantidad_a_descontar)
            if producto.pro_stock >= cantidad_a_descontar:
                producto.pro_stock -= cantidad_a_descontar
                producto.save()
                historial_data = {
                    'his_usuario': usu_id,
                    'his_producto': producto_id,
                    'his_fecha_modificacion': datetime.now(),
                    'his_modificacion': 'Producto descontado',
                    'his_cantidad': cantidad_a_descontar,
                    'his_observacion': 'Producto descontado',
                    'his_cliente': None,
                }
            historial_serializer = HistorialSerializer(data=historial_data)
            if historial_serializer.is_valid():
                historial_serializer.save()
                return Response({'estado': True, 'mensaje': f'Se agregaron {cantidad_a_descontar} unidades al producto.'})
            else:
                return Response({'estado': False, 'mensaje': 'Stock insuficiente para realizar el descuento.'})
        except Productos.DoesNotExist:
            return Response({'estado': False, 'mensaje': 'Producto no encontrado'})

    return Response({'estado': False, 'mensaje': 'Método no permitido'})


@api_view(["POST"])
def Agregar_Stock(request):
    if request.method == "POST":
        producto_id = request.data.get("producto_id")
        cantidad_a_agregar = request.data.get("cantidad_a_agregar")
        usu_id = request.data.get("usu_id")
        if cantidad_a_agregar is None:
            return Response({'estado': False, 'mensaje': 'Cantidad a agregar no especificada'})

        try:
            producto = Productos.objects.get(pro_id=producto_id)
            producto.pro_stock = int(producto.pro_stock)
            cantidad_a_agregar = int(cantidad_a_agregar)
            producto.pro_stock += cantidad_a_agregar
            producto.save()

            historial_data = {
                'his_usuario': usu_id,
                'his_producto': producto_id,
                'his_fecha_modificacion': datetime.now(),
                'his_modificacion': 'Producto agregado',
                'his_cantidad': cantidad_a_agregar,
                'his_observacion': 'Producto agregado',
                'his_cliente': None,
            }
            historial_serializer = HistorialSerializer(data=historial_data)
            if historial_serializer.is_valid():
                historial_serializer.save()
                return Response({'estado': True, 'mensaje': f'Se agregaron {cantidad_a_agregar} unidades al producto.'})
            else:
                return Response({'estado': False, 'mensaje': 'Error al agregar historial'})

        except Productos.DoesNotExist:
            return Response({'estado': False, 'mensaje': 'Producto no encontrado'})

    return Response({'estado': False, 'mensaje': 'Método no permitido'})


@api_view(["POST"])
def Modificar_Producto(request):
    if request.method == "POST":
        producto_id = request.data.get("producto_id")
        nuevo_nombre = request.data.get("nuevo_nombre")
        nueva_marca = request.data.get("nueva_marca")
        nuevo_stock = request.data.get("nuevo_stock")
        nuevo_precio = request.data.get("nuevo_precio")

        try:

            producto = Productos.objects.get(pro_id=producto_id)

            producto.pro_nombre = nuevo_nombre
            producto.pro_marca__mar_nombre = nueva_marca
            producto.pro_stock = nuevo_stock
            producto.pro_precio = nuevo_precio

            producto.save()

            return Response({'estado': True, 'mensaje': 'Producto modificado exitosamente.'})
        except Productos.DoesNotExist:
            return Response({'estado': False, 'mensaje': 'Producto no encontrado'})

    return Response({'estado': False, 'mensaje': 'Método no permitido'})


@api_view(["POST"])
def Agregar_Producto(request):
    if request.method == "POST":
        print(request.data)
        serializer = ProductoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'estado': True, 'mensaje': 'Producto agregado con éxito'})
        return Response({'estado': False, 'mensaje': 'Datos no válidos'})
    return Response({'estado': False, 'mensaje': 'Método no permitido'})


@api_view(["GET"])
def Obtener_Marcas(request):
    if request.method == "GET":
        marcas = Marcas.objects.all()
        serializer = MarcaSerializer(marcas, many=True)
        return Response({'estado': True, 'marcas': serializer.data})
    return Response({'estado': False, 'mensaje': 'Método no permitido'})


@api_view(["GET"])
def obtener_historial_agregan(request):
    if request.method == "GET":
        resultados = Historial.objects.filter(his_modificacion='Producto agregado') \
            .values('his_producto__pro_nombre') \
            .annotate(producto=F('his_producto__pro_nombre'), total=Coalesce(Sum('his_cantidad'), 0)) \
            .values('producto', 'total')
        return Response({'estado': True, 'data': resultados})
    return Response({'estado': False, 'mensaje': 'Método no permitido'})


@api_view(["GET"])
def obtener_historial_agregan_pesos(request):
    if request.method == "GET":
        resultados = Historial.objects.filter(his_modificacion='Producto agregado') \
            .values('his_producto__pro_nombre') \
            .annotate(producto=F('his_producto__pro_nombre'), cantidad=Coalesce(Sum('his_cantidad'), 0), precio=F('his_producto__pro_precio')) \
            .values('producto', 'cantidad', 'precio')
        if resultados:
            return Response({'estado': True, 'data': resultados})
    return Response({'estado': False, 'mensaje': 'Método no permitido'})


@api_view(["GET"])
def obtener_historial_descuentan(request):
    if request.method == "GET":
        resultados = Historial.objects.filter(his_modificacion='Producto descontado') \
            .values('his_producto__pro_nombre') \
            .annotate(producto=F('his_producto__pro_nombre'), total=Coalesce(Sum('his_cantidad'), 0)) \
            .values('producto', 'total')
        return Response({'estado': True, 'data': resultados})
    return Response({'estado': False, 'mensaje': 'Método no permitido'})
