from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import HistoriaClinicaViewSet

router = DefaultRouter()

urlpatterns = router.urls + [
    path(
        'historia/paciente/<int:pk>/',
        HistoriaClinicaViewSet.as_view({'get': 'historia_paciente'})
    ),
    path(
        'historia/antecedentes/<int:id_medico>/<int:id_paciente>/',
        HistoriaClinicaViewSet.as_view({'put': 'actualizar_antecedentes'})
    ),
    path(
        'historia/completa/<int:id_medico>/<int:id_paciente>/',
        HistoriaClinicaViewSet.as_view({'get': 'historia_completa'})
    ),
]
