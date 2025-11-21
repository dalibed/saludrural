import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { LogOut, User, Home } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login', { replace: true });
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
      // Aun así, redirigir al login
      navigate('/login', { replace: true });
    }
  };

  return (
    <nav className="bg-white border-b border-gray-100">
      <div className="px-6 py-4 flex justify-between items-center">
        <Link to="/" className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-2xl bg-primary-600 text-white font-bold flex items-center justify-center">
            SR
          </div>
          <div>
            <p className="text-lg font-bold text-dark-700">Salud Rural</p>
            <p className="text-xs text-dark-400 -mt-1">Panel interno</p>
          </div>
        </Link>
        <div className="flex items-center space-x-4">
          <Link
            to="/"
            className="hidden md:inline-flex items-center px-4 py-2 text-sm font-semibold text-primary-600 bg-primary-50 rounded-xl"
          >
            <Home className="w-4 h-4 mr-2" />
            Portal público
          </Link>
          <div className="flex items-center space-x-2 text-dark-600 bg-gray-50 px-4 py-2 rounded-xl">
            <User className="w-5 h-5" />
            <div className="flex flex-col text-sm">
              <span className="font-semibold">
                {user?.nombre} {user?.apellidos}
              </span>
              <span className="text-dark-400 text-xs">{user?.rol}</span>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center space-x-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-xl transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Salir</span>
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
