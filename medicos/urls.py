from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import MedicoViewSet

router = DefaultRouter()
router.register(r'medicos', MedicoViewSet, basename='medicos')

urlpatterns = router.urls + [

    path(
        'medicos/estado/<int:pk>/',
        MedicoViewSet.as_view({'get': 'estado'})
    ),

    path(
        'medicos/listar-estado/<str:estado>/',
        MedicoViewSet.as_view({'get': 'list_by_estado'})
    ),
]
