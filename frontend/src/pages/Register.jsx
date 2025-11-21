import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { usuarioService } from '../services/api';
import { HeartPulse } from 'lucide-react';

const initialForm = {
  nombre: '',
  apellidos: '',
  documento: '',
  correo: '',
  telefono: '',
  fecha_nacimiento: '',
  contrasena: '',
  rol: 'Paciente',
  grupo_sanguineo: '',
  seguro_medico: '',
  contacto_emergencia: '',
  telefono_emergencia: '',
  licencia: '',
  anios_experiencia: '',
  descripcion_perfil: '',
};

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState(initialForm);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const handleChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage({ type: '', text: '' });

    try {
      setLoading(true);
      const payload = { ...formData };
      if (payload.rol !== 'Paciente') {
        delete payload.grupo_sanguineo;
        delete payload.seguro_medico;
        delete payload.contacto_emergencia;
        delete payload.telefono_emergencia;
      }
      if (payload.rol !== 'Medico') {
        delete payload.licencia;
        delete payload.anios_experiencia;
        delete payload.descripcion_perfil;
      } else if (payload.anios_experiencia === '') {
        payload.anios_experiencia = null;
      }

      await usuarioService.create(payload);
      setMessage({
        type: 'success',
        text: 'Registro exitoso. Revisa tu correo y luego inicia sesión.',
      });
      setTimeout(() => navigate('/login'), 1500);
    } catch (error) {
      console.error('Error registrando usuario', error);
      setMessage({
        type: 'error',
        text:
          error.response?.data?.detail ||
          'No pudimos completar tu registro. Revisa la información e inténtalo nuevamente.',
      });
    } finally {
      setLoading(false);
    }
  };

  const isPaciente = formData.rol === 'Paciente';
  const isMedico = formData.rol === 'Medico';

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-accent-50 flex items-center justify-center p-4">
      <div className="bg-white w-full max-w-4xl rounded-3xl shadow-2xl border border-primary-100 p-10">
        <div className="flex items-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-primary-600 text-white flex items-center justify-center">
            <HeartPulse className="w-7 h-7" />
          </div>
          <div className="ml-4">
            <p className="text-sm uppercase tracking-wide text-dark-400">Únete a Salud Rural</p>
            <h1 className="text-3xl font-bold text-dark-800">Crear cuenta</h1>
          </div>
        </div>

        {message.text && (
          <div
            className={`mb-6 rounded-2xl px-4 py-3 text-sm font-medium ${
              message.type === 'success'
                ? 'bg-green-50 text-green-800 border border-green-200'
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}
          >
            {message.text}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-dark-500 mb-2">Nombre</label>
              <input
                className="input"
                value={formData.nombre}
                onChange={(e) => handleChange('nombre', e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-dark-500 mb-2">Apellidos</label>
              <input
                className="input"
                value={formData.apellidos}
                onChange={(e) => handleChange('apellidos', e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-dark-500 mb-2">Documento</label>
              <input
                className="input"
                value={formData.documento}
                onChange={(e) => handleChange('documento', e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-dark-500 mb-2">Fecha de nacimiento</label>
              <input
                type="date"
                className="input"
                value={formData.fecha_nacimiento}
                onChange={(e) => handleChange('fecha_nacimiento', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-dark-500 mb-2">Correo</label>
              <input
                type="email"
                className="input"
                value={formData.correo}
                onChange={(e) => handleChange('correo', e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-dark-500 mb-2">Teléfono</label>
              <input
                className="input"
                value={formData.telefono}
                onChange={(e) => handleChange('telefono', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-dark-500 mb-2">Contraseña</label>
              <input
                type="password"
                className="input"
                value={formData.contrasena}
                onChange={(e) => handleChange('contrasena', e.target.value)}
                required
                minLength={8}
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-dark-500 mb-2">Rol</label>
              <select
                className="input"
                value={formData.rol}
                onChange={(e) => handleChange('rol', e.target.value)}
              >
                <option value="Paciente">Paciente</option>
                <option value="Medico">Médico</option>
              </select>
            </div>
          </div>

          {isPaciente && (
            <div className="border border-gray-100 rounded-2xl p-4 grid grid-cols-1 md:grid-cols-2 gap-4 bg-primary-50/40">
              <p className="md:col-span-2 text-sm font-semibold text-primary-700">
                Información clínica opcional
              </p>
              <input
                className="input"
                placeholder="Grupo sanguíneo"
                value={formData.grupo_sanguineo}
                onChange={(e) => handleChange('grupo_sanguineo', e.target.value)}
              />
              <input
                className="input"
                placeholder="Seguro médico"
                value={formData.seguro_medico}
                onChange={(e) => handleChange('seguro_medico', e.target.value)}
              />
              <input
                className="input"
                placeholder="Contacto de emergencia"
                value={formData.contacto_emergencia}
                onChange={(e) => handleChange('contacto_emergencia', e.target.value)}
              />
              <input
                className="input"
                placeholder="Teléfono emergencia"
                value={formData.telefono_emergencia}
                onChange={(e) => handleChange('telefono_emergencia', e.target.value)}
              />
            </div>
          )}

          {isMedico && (
            <div className="border border-gray-100 rounded-2xl p-4 grid grid-cols-1 md:grid-cols-2 gap-4 bg-accent-50/40">
              <p className="md:col-span-2 text-sm font-semibold text-accent-700">
                Información profesional
              </p>
              <input
                className="input"
                placeholder="Número de licencia"
                value={formData.licencia}
                onChange={(e) => handleChange('licencia', e.target.value)}
                required
              />
              <input
                type="number"
                min={0}
                className="input"
                placeholder="Años de experiencia"
                value={formData.anios_experiencia}
                onChange={(e) => handleChange('anios_experiencia', e.target.value)}
              />
              <textarea
                className="input md:col-span-2"
                rows={3}
                placeholder="Descripción de tu perfil"
                value={formData.descripcion_perfil}
                onChange={(e) => handleChange('descripcion_perfil', e.target.value)}
              />
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary w-full py-3"
            disabled={loading}
          >
            {loading ? 'Creando cuenta...' : 'Registrarme'}
          </button>
        </form>

        <p className="text-center text-sm text-dark-400 mt-6">
          ¿Ya tienes cuenta?{' '}
          <Link to="/login" className="text-primary-600 font-semibold">
            Inicia sesión aquí
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Register;

