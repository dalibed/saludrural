from rest_framework.routers import DefaultRouter
from .views import AdministradorViewSet

router = DefaultRouter()
router.register(r'administrador', AdministradorViewSet, basename='administrador')

urlpatterns = router.urls
