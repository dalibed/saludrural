"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

urlpatterns = [
    path('admin/', admin.site.urls),
    

    # Cada módulo es 100 % independiente
    path('api/', include('usuarios.urls')),
    path('api/', include('pacientes.urls')),
    path('api/', include('medicos.urls')),
    path('api/', include('administrador.urls')),
    path('api/',include('tp_documentos.urls')),
    path('api/',include('documentos.urls')),
    path('api/',include('agenda.urls')),
    path('api/',include('citas.urls')),
    path('api/', include('historia_clinica.urls')),
    path('api/', include('historia_entrada.urls')),
    path('api/', include('diccionario.urls')),
    path('api/', include('videollamada.urls')),
    path('api/', include('especialidad.urls')),
    path('api/', include('notificaciones.urls')),
]
