from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import TipoDocumentoViewSet

router = DefaultRouter()
router.register(r'tipodocumento', TipoDocumentoViewSet, basename='tipodocumento')

urlpatterns = router.urls
