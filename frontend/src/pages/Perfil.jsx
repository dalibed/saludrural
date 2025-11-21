import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/api';
import { User, Mail, Phone, Calendar, Lock, Save } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const Perfil = () => {
  const { user } = useAuth();
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [message, setMessage] = useState({ type: '', text: '' });

  const handleChangePassword = async (e) => {
    e.preventDefault();

    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage({
        type: 'error',
        text: 'Las contraseñas no coinciden',
      });
      return;
    }

    if (passwordData.new_password.length < 8) {
      setMessage({
        type: 'error',
        text: 'La contraseña debe tener al menos 8 caracteres',
      });
      return;
    }

    try {
      await authService.changePassword(
        passwordData.old_password,
        passwordData.new_password
      );
      setMessage({
        type: 'success',
        text: 'Contraseña actualizada correctamente',
      });
      setPasswordData({
        old_password: '',
        new_password: '',
        confirm_password: '',
      });
      setShowPasswordForm(false);
    } catch (error) {
      setMessage({
        type: 'error',
        text:
          error.response?.data?.detail ||
          'Error al cambiar la contraseña. Verifica tu contraseña actual.',
      });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Mi Perfil</h1>
        <p className="text-gray-600">Gestiona tu información personal</p>
      </div>

      {/* Información del Usuario */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Información Personal
        </h2>
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center">
              <User className="w-10 h-10 text-primary-600" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-900">
                {user?.nombre} {user?.apellidos}
              </h3>
              <p className="text-gray-600">{user?.rol}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            <div className="flex items-start space-x-3">
              <Mail className="w-5 h-5 text-gray-400 mt-1" />
              <div>
                <p className="text-sm font-medium text-gray-700">Correo</p>
                <p className="text-gray-900">{user?.correo || 'No disponible'}</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <Phone className="w-5 h-5 text-gray-400 mt-1" />
              <div>
                <p className="text-sm font-medium text-gray-700">Teléfono</p>
                <p className="text-gray-900">{user?.telefono || 'No disponible'}</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <Calendar className="w-5 h-5 text-gray-400 mt-1" />
              <div>
                <p className="text-sm font-medium text-gray-700">
                  Fecha de Nacimiento
                </p>
                <p className="text-gray-900">
                  {user?.fecha_nacimiento
                    ? format(new Date(user.fecha_nacimiento), 'dd MMM yyyy', {
                        locale: es,
                      })
                    : 'No disponible'}
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <User className="w-5 h-5 text-gray-400 mt-1" />
              <div>
                <p className="text-sm font-medium text-gray-700">Documento</p>
                <p className="text-gray-900">{user?.documento || 'No disponible'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Cambiar Contraseña */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">Seguridad</h2>
          <button
            onClick={() => setShowPasswordForm(!showPasswordForm)}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Lock className="w-4 h-4" />
            <span>Cambiar Contraseña</span>
          </button>
        </div>

        {message.text && (
          <div
            className={`mb-4 p-4 rounded-lg ${
              message.type === 'success'
                ? 'bg-green-50 text-green-800 border border-green-200'
                : 'bg-red-50 text-red-800 border border-red-200'
            }`}
          >
            {message.text}
          </div>
        )}

        {showPasswordForm && (
          <form onSubmit={handleChangePassword} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Contraseña Actual
              </label>
              <input
                type="password"
                value={passwordData.old_password}
                onChange={(e) =>
                  setPasswordData({
                    ...passwordData,
                    old_password: e.target.value,
                  })
                }
                className="input"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nueva Contraseña
              </label>
              <input
                type="password"
                value={passwordData.new_password}
                onChange={(e) =>
                  setPasswordData({
                    ...passwordData,
                    new_password: e.target.value,
                  })
                }
                className="input"
                required
                minLength={8}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Confirmar Nueva Contraseña
              </label>
              <input
                type="password"
                value={passwordData.confirm_password}
                onChange={(e) =>
                  setPasswordData({
                    ...passwordData,
                    confirm_password: e.target.value,
                  })
                }
                className="input"
                required
                minLength={8}
              />
            </div>

            <div className="flex space-x-3 pt-2">
              <button
                type="button"
                onClick={() => {
                  setShowPasswordForm(false);
                  setMessage({ type: '', text: '' });
                }}
                className="btn btn-secondary"
              >
                Cancelar
              </button>
              <button type="submit" className="btn btn-primary flex items-center space-x-2">
                <Save className="w-4 h-4" />
                <span>Guardar</span>
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default Perfil;
