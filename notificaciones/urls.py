from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import NotificacionViewSet

router = DefaultRouter()
# No register porque no hay CRUD principal

urlpatterns = [
    path(
        'notificaciones/paciente/<int:pk>/',
        NotificacionViewSet.as_view({'get': 'list_paciente'})
    ),
    path(
        'notificaciones/medico/<int:pk>/',
        NotificacionViewSet.as_view({'get': 'list_medico'})
    ),
]
