from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import HistoriaEntradaViewSet

router = DefaultRouter()
router.register(r'historia-entradas', HistoriaEntradaViewSet, basename='historia-entradas')

urlpatterns = router.urls + [
    path(
        'historia/entrada/paciente/<int:pk>/',
        HistoriaEntradaViewSet.as_view({'get': 'list_paciente'})
    ),
    path(
        'historia/entrada/medico/<int:pk>/',
        HistoriaEntradaViewSet.as_view({'get': 'list_medico'})
    ),
]
