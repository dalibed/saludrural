from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CitaViewSet

router = DefaultRouter()
router.register(r'citas', CitaViewSet, basename='citas')

urlpatterns = router.urls + [
    path('citas/cancelar/<int:pk>/', CitaViewSet.as_view({'put': 'cancelar'})),
    path('citas/completar/<int:pk>/', CitaViewSet.as_view({'put': 'completar'})),  # 👈 NUEVA RUTA
    path('citas/paciente/<int:pk>/', CitaViewSet.as_view({'get': 'citas_paciente'})),
    path('citas/medico/<int:pk>/', CitaViewSet.as_view({'get': 'citas_medico'})),
]
