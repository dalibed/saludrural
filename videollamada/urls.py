from django.urls import path
from .views import VideollamadaViewSet

urlpatterns = [
    path('videollamada/<int:pk>/', VideollamadaViewSet.as_view({'get': 'retrieve'})),
    path('videollamada/configurar/<int:pk>/', VideollamadaViewSet.as_view({'post': 'crear'})),
]
