"""Back_Bodega URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from bodega import views
from django.urls import path


urlpatterns = [
    path('Traer_usuarios/', views.Traer_usuarios),
    path('Iniciar_sesion/', views.Iniciar_sesion),
    path('Traer_Productos/', views.Traer_Productos),
    path('Descontar_Producto/', views.Descontar_Producto),
    path('Agregar_Producto/', views.Agregar_Producto),
    path('Agregar_Stock/', views.Agregar_Stock),
    path('Modificar_Producto/', views.Modificar_Producto),
    path('Obtener_Marcas/', views.Obtener_Marcas),
    path('obtener_historial_agregan/', views.obtener_historial_agregan),
    path('obtener_historial_descuentan/', views.obtener_historial_descuentan),
    path('obtener_historial_agregan_pesos/',
         views.obtener_historial_agregan_pesos),
]
