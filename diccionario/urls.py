from rest_framework.routers import DefaultRouter
from .views import DiccionarioViewSet

router = DefaultRouter()
router.register(r'diccionario', DiccionarioViewSet, basename='diccionario')

urlpatterns = router.urls
