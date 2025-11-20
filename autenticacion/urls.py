"""
URLs para el módulo de Autenticación

Define las rutas de los endpoints de autenticación.
Usa DefaultRouter de DRF para generar automáticamente las rutas REST.

Rutas generadas:
- POST   /api/auth/login/           - Iniciar sesión
- POST   /api/auth/logout/          - Cerrar sesión
- GET    /api/auth/me/              - Info usuario autenticado
- POST   /api/auth/change-password/ - Cambiar contraseña
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet

# Crear router para generar rutas automáticamente
router = DefaultRouter()

# Registrar el viewset
# - 'auth' es el prefijo de la URL
# - basename se usa para nombrar las rutas en reverses
router.register(r'auth', AuthViewSet, basename='auth')

# Las rutas se exportan para incluirlas en backend/urls.py
urlpatterns = router.urls

# =============================================================================
# EJEMPLO DE USO EN EL FRONTEND
# =============================================================================
#
# // Login
# fetch('/api/auth/login/', {
#   method: 'POST',
#   headers: {'Content-Type': 'application/json'},
#   body: JSON.stringify({
#     correo: 'usuario@example.com',
#     contrasena: 'password123'
#   })
# })
# .then(res => res.json())
# .then(data => {
#   localStorage.setItem('access_token', data.access);
#   localStorage.setItem('refresh_token', data.refresh);
# });
#
# // Request autenticado
# fetch('/api/citas/paciente/1/', {
#   headers: {
#     'Authorization': `Bearer ${localStorage.getItem('access_token')}`
#   }
# })
#
# =============================================================================