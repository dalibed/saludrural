import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Calendar,
  Users,
  Stethoscope,
  UserCircle,
  BookOpen,
  ClipboardCheck,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const basePath = '/app';

const Sidebar = () => {
  const { user } = useAuth();

  const menuItems = [
    { path: `${basePath}/dashboard`, icon: LayoutDashboard, label: 'Dashboard' },
    { path: `${basePath}/citas`, icon: Calendar, label: 'Citas' },
  ];

  if (user?.rol === 'Paciente') {
    menuItems.push(
      { path: `${basePath}/historia`, icon: BookOpen, label: 'Historia clínica' },
      { path: `${basePath}/medicos`, icon: Stethoscope, label: 'Médicos aprobados' },
    );
  }

  if (user?.rol === 'Medico') {
    menuItems.push(
      { path: `${basePath}/agenda`, icon: Calendar, label: 'Mi agenda' },
      { path: `${basePath}/medicos`, icon: Stethoscope, label: 'Directorio' },
    );
  }

  if (user?.rol === 'Administrador') {
    menuItems.push(
      { path: `${basePath}/pacientes`, icon: Users, label: 'Pacientes' },
      { path: `${basePath}/medicos`, icon: Stethoscope, label: 'Médicos' },
      { path: `${basePath}/validaciones`, icon: ClipboardCheck, label: 'Validar documentos' },
    );
  }

  menuItems.push({ path: `${basePath}/perfil`, icon: UserCircle, label: 'Mi Perfil' });

  return (
    <aside className="w-64 bg-white shadow-md min-h-screen border-r border-gray-100">
      <nav className="p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-4 py-3 rounded-xl transition-colors ${
                    isActive ? 'bg-primary-600 text-white' : 'text-dark-500 hover:bg-primary-50'
                  }`
                }
              >
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
