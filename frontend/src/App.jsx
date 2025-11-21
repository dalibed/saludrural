import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Citas from './pages/Citas';
import Pacientes from './pages/Pacientes';
import Medicos from './pages/Medicos';
import Perfil from './pages/Perfil';
import HistoriaClinica from './pages/HistoriaClinica';
import Home from './pages/Home';
import MedicosPublic from './pages/MedicosPublic';
import Diccionario from './pages/Diccionario';
import AgendaMedico from './pages/AgendaMedico';
import AdminValidaciones from './pages/AdminValidaciones';
import Layout from './components/Layout';
import PublicLayout from './components/PublicLayout';

// Componente para proteger rutas que requieren autenticación
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Componente para rutas públicas (redirige al dashboard si ya está autenticado)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando...</p>
        </div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/app/dashboard" replace />;
  }

  return children;
};

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<PublicLayout />}>
        <Route index element={<Home />} />
        <Route path="medicos" element={<MedicosPublic />} />
        <Route path="diccionario" element={<Diccionario />} />
      </Route>

      <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/app/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="citas" element={<Citas />} />
        <Route path="pacientes" element={<Pacientes />} />
        <Route path="medicos" element={<Medicos />} />
        <Route path="perfil" element={<Perfil />} />
        <Route path="historia" element={<HistoriaClinica />} />
        <Route path="agenda" element={<AgendaMedico />} />
        <Route path="validaciones" element={<AdminValidaciones />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
}

export default App;
