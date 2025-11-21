import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

// Crear instancia de axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar el token de autenticación
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores y refrescar tokens
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si el error es 401 y no hemos intentado refrescar el token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);
          originalRequest.headers.Authorization = `Bearer ${access}`;

          return api(originalRequest);
        }
      } catch (refreshError) {
        // Si falla el refresh, limpiar tokens y redirigir al login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Servicios de autenticación
export const authService = {
  login: async (correo, contrasena) => {
    const response = await api.post('/auth/login/', { correo, contrasena });
    return response.data;
  },

  logout: async () => {
    try {
      await api.post('/auth/logout/', {
        refresh_token: localStorage.getItem('refresh_token'),
      });
    } catch (error) {
      console.error('Error al hacer logout:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },

  getMe: async () => {
    const response = await api.get('/auth/me/');
    return response.data;
  },

  changePassword: async (oldPassword, newPassword) => {
    const response = await api.post('/auth/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
    });
    return response.data;
  },
};

// Servicios de pacientes
export const pacienteService = {
  getAll: async () => {
    const response = await api.get('/pacientes/');
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/pacientes/${id}/`);
    return response.data;
  },

  create: async (data) => {
    const response = await api.post('/pacientes/', data);
    return response.data;
  },

  update: async (id, data) => {
    const response = await api.put(`/pacientes/${id}/`, data);
    return response.data;
  },

  delete: async (id) => {
    const response = await api.delete(`/pacientes/${id}/`);
    return response.data;
  },
};

// Servicios de médicos
export const medicoService = {
  getAll: async () => {
    const response = await api.get('/medicos/');
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/medicos/${id}/`);
    return response.data;
  },

  getByEstado: async (estado) => {
    const response = await api.get(`/medicos/listar-estado/${estado}/`);
    return response.data;
  },
};

// Servicios de citas
export const citaService = {
  getAll: async () => {
    const response = await api.get('/citas/');
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/citas/${id}/`);
    return response.data;
  },

  create: async (data) => {
    const response = await api.post('/citas/', data);
    return response.data;
  },

  update: async (id, data) => {
    const response = await api.put(`/citas/${id}/`, data);
    return response.data;
  },

  cancelar: async (id) => {
    const response = await api.put(`/citas/cancelar/${id}/`);
    return response.data;
  },

  completar: async (id) => {
    const response = await api.put(`/citas/completar/${id}/`);
    return response.data;
  },

  getByPaciente: async (pacienteId) => {
    const response = await api.get(`/citas/paciente/${pacienteId}/`);
    return response.data;
  },

  getByMedico: async (medicoId) => {
    const response = await api.get(`/citas/medico/${medicoId}/`);
    return response.data;
  },
};

// Servicios de agenda
export const agendaService = {
  getAll: async () => {
    const response = await api.get('/agenda/');
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/agenda/${id}/`);
    return response.data;
  },

  create: async (data) => {
    const response = await api.post('/agenda/', data);
    return response.data;
  },

  getDisponibles: async (fecha, medicoId) => {
    const response = await api.get('/agenda/', {
      params: { fecha, medico_id: medicoId, disponible: true },
    });
    return response.data;
  },
};

export default api;
