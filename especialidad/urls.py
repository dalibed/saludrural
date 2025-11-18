from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import EspecialidadViewSet

router = DefaultRouter()
router.register(r'especialidades', EspecialidadViewSet, basename='especialidades')

urlpatterns = router.urls + [
    path(
        'especialidades/asignar/',
        EspecialidadViewSet.as_view({'post': 'asignar'})
    ),
    path(
        'especialidades/medico/<int:pk>/',
        EspecialidadViewSet.as_view({'get': 'listar_por_medico'})
    ),
]
