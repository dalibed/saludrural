import React, { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const navLinks = [
  { label: 'Inicio', to: '/' },
  { label: 'Médicos', to: '/medicos' },
  { label: 'Diccionario', to: '/diccionario' },
];

const PublicNavbar = () => {
  const [open, setOpen] = useState(false);
  const { isAuthenticated } = useAuth();

  const renderLinks = (onClick = () => {}) =>
    navLinks.map((link) => (
      <NavLink
        key={link.to}
        to={link.to}
        onClick={onClick}
        className={({ isActive }) =>
          `text-sm font-semibold px-4 py-2 rounded-full transition-colors ${
            isActive
              ? 'text-white bg-primary-600'
              : 'text-dark-500 hover:text-primary-600 hover:bg-primary-50'
          }`
        }
      >
        {link.label}
      </NavLink>
    ));

  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur border-b border-gray-100">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-3">
          <div className="w-12 h-12 rounded-2xl bg-primary-600 text-white font-bold flex items-center justify-center">
            SR
          </div>
          <div>
            <p className="text-lg font-bold text-dark-700">Salud Rural</p>
            <p className="text-sm text-dark-400">Cuidamos tu bienestar</p>
          </div>
        </Link>

        <nav className="hidden md:flex items-center space-x-2">{renderLinks()}</nav>

        <div className="hidden md:flex items-center space-x-3">
          {isAuthenticated ? (
            <Link to="/app/dashboard" className="btn btn-primary">
              Ir al panel
            </Link>
          ) : (
            <>
              <Link to="/login" className="btn btn-ghost">
                Ingresar
              </Link>
              <Link to="/register" className="btn btn-primary">
                Registrarme
              </Link>
            </>
          )}
        </div>

        <button
          className="md:hidden text-dark-600"
          onClick={() => setOpen((prev) => !prev)}
          aria-label="Menú"
        >
          {open ? <X className="w-7 h-7" /> : <Menu className="w-7 h-7" />}
        </button>
      </div>

      {open && (
        <div className="md:hidden border-t border-gray-100 bg-white px-4 pb-4 space-y-3">
          <div className="flex flex-col space-y-2">{renderLinks(() => setOpen(false))}</div>
          {isAuthenticated ? (
            <Link
              to="/app/dashboard"
              className="btn btn-primary w-full"
              onClick={() => setOpen(false)}
            >
              Ir al panel
            </Link>
          ) : (
            <div className="space-y-2">
              <Link to="/login" className="btn btn-secondary w-full" onClick={() => setOpen(false)}>
                Ingresar
              </Link>
              <Link to="/register" className="btn btn-primary w-full" onClick={() => setOpen(false)}>
                Registrarme
              </Link>
            </div>
          )}
        </div>
      )}
    </header>
  );
};

export default PublicNavbar;

