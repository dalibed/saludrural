import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Verificar si hay un token guardado al cargar la app
    const token = localStorage.getItem('access_token');
    if (token) {
      checkAuth();
    } else {
      setLoading(false);
    }
  }, []);

  const checkAuth = async () => {
    try {
      setLoading(true);
      const userData = await authService.getMe();
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Error al verificar autenticación:', error);
      // Si hay error (token inválido o expirado), limpiar todo
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (correo, contrasena) => {
    try {
      const data = await authService.login(correo, contrasena);
      
      // Verificar que la respuesta tenga los tokens necesarios
      if (!data.access || !data.refresh) {
        throw new Error('Respuesta del servidor inválida: faltan tokens');
      }
      
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      
      // El backend ya devuelve la información del usuario en la respuesta
      if (data.usuario) {
        setUser(data.usuario);
        setIsAuthenticated(true);
      } else {
        // Si no viene en la respuesta, obtenerla
        try {
          const userData = await authService.getMe();
          setUser(userData);
          setIsAuthenticated(true);
        } catch (meError) {
          console.error('Error al obtener información del usuario:', meError);
          // Aun así, consideramos el login exitoso si tenemos tokens
          setIsAuthenticated(true);
        }
      }
      
      return { success: true };
    } catch (error) {
      console.error('Error al iniciar sesión:', error);
      
      // Limpiar tokens en caso de error
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      let errorMessage = 'Error al iniciar sesión';
      
      if (error.response) {
        // Error de respuesta del servidor
        errorMessage = error.response.data?.detail || 
                      error.response.data?.message || 
                      `Error ${error.response.status}: ${error.response.statusText}`;
      } else if (error.request) {
        // Error de red (sin respuesta del servidor)
        errorMessage = 'No se pudo conectar con el servidor. Verifica que el backend esté corriendo.';
      } else if (error.message) {
        // Otro tipo de error
        errorMessage = error.message;
      }
      
      return {
        success: false,
        error: errorMessage,
      };
    }
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
