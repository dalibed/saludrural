from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DocumentoViewSet

router = DefaultRouter()
router.register(r'documentos', DocumentoViewSet, basename='documentos')

urlpatterns = router.urls + [
    path(
        'documentos/<int:pk>/validar/',
        DocumentoViewSet.as_view({'post': 'validate'}),
        name='documento-validar'
    ),
]
