from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AgendaViewSet

router = DefaultRouter()
router.register(r'agenda', AgendaViewSet, basename='agenda')

urlpatterns = router.urls + [
    path('agenda/disponible/<int:pk>/', AgendaViewSet.as_view({'get': 'disponible'})),
    path('agenda/toggle/<int:pk>/', AgendaViewSet.as_view({'put': 'toggle'})),
]
