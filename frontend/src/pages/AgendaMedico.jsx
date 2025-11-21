import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { agendaService, medicoService } from '../services/api';
import { Calendar, Clock, AlertTriangle } from 'lucide-react';

const AgendaMedico = () => {
  const { user } = useAuth();
  const [medicoInfo, setMedicoInfo] = useState(null);
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [message, setMessage] = useState('');
  const [formData, setFormData] = useState({
    fecha: '',
    hora_inicio: '',
    hora_fin: '',
  });

  const isMedico = user?.rol === 'Medico';

  useEffect(() => {
    if (isMedico) {
      loadData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isMedico]);

  const loadData = async () => {
    try {
      setLoading(true);
      const info = await medicoService.getById(user.id_usuario);
      setMedicoInfo(info);
      await loadSlots();
    } catch (error) {
      console.error('Error al cargar información del médico', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSlots = async () => {
    if (!isMedico) return;
    try {
      setLoadingSlots(true);
      const data = await agendaService.getByMedico(user.id_usuario);
      setSlots(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error al cargar agenda', error);
    } finally {
      setLoadingSlots(false);
    }
  };

  const handleCreateSlots = async (e) => {
    e.preventDefault();
    setMessage('');

    try {
      await agendaService.create({
        id_usuario_medico: user.id_usuario,
        fecha: formData.fecha,
        hora_inicio: formData.hora_inicio,
        hora_fin: formData.hora_fin,
      });
      setFormData({ fecha: '', hora_inicio: '', hora_fin: '' });
      setMessage('Agenda creada correctamente.');
      await loadSlots();
    } catch (error) {
      console.error('Error al crear agenda', error);
      setMessage(
        error.response?.data?.detail ||
          'No se pudo crear la agenda. Verifica la información e intenta nuevamente.'
      );
    }
  };

  const toggleSlot = async (slot) => {
    try {
      await agendaService.toggle(slot.id_agenda, {
        id_usuario_medico: user.id_usuario,
        disponible: !slot.disponible,
      });
      await loadSlots();
    } catch (error) {
      console.error('Error al actualizar slot', error);
    }
  };

  if (!isMedico) {
    return <Navigate to="/app/dashboard" replace />;
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
      </div>
    );
  }

  const isApproved = medicoInfo?.estado_validacion === 'Aprobado';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-dark-800">Mi agenda</h1>
          <p className="text-dark-500">Gestiona tus espacios disponibles</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="chip">{medicoInfo?.estado_validacion || 'Pendiente'}</span>
        </div>
      </div>

      {!isApproved && (
        <div className="card border border-yellow-200 bg-yellow-50 flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 text-yellow-600 mt-1" />
          <p className="text-sm text-yellow-700">
            Tus documentos aún no han sido aprobados. El administrador debe validar tu perfil antes
            de que puedas abrir agenda. Revisa la sección de perfil para completar la documentación.
          </p>
        </div>
      )}

      <div className={`card ${!isApproved ? 'opacity-50 pointer-events-none' : ''}`}>
        <h2 className="text-xl font-bold text-dark-700 mb-4">Crear horarios</h2>
        {message && (
          <div className="mb-4 text-sm text-primary-700 bg-primary-50 rounded-xl px-4 py-2">
            {message}
          </div>
        )}
        <form className="grid grid-cols-1 md:grid-cols-3 gap-4" onSubmit={handleCreateSlots}>
          <div>
            <label className="block text-sm font-medium text-dark-500 mb-2">Fecha</label>
            <input
              type="date"
              className="input"
              value={formData.fecha}
              onChange={(e) => setFormData((prev) => ({ ...prev, fecha: e.target.value }))}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-dark-500 mb-2">Hora inicio</label>
            <input
              type="time"
              className="input"
              value={formData.hora_inicio}
              onChange={(e) => setFormData((prev) => ({ ...prev, hora_inicio: e.target.value }))}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-dark-500 mb-2">Hora fin</label>
            <input
              type="time"
              className="input"
              value={formData.hora_fin}
              onChange={(e) => setFormData((prev) => ({ ...prev, hora_fin: e.target.value }))}
              required
            />
          </div>
          <div className="md:col-span-3 flex justify-end">
            <button type='submit' className="btn btn-primary" disabled={loadingSlots}>
              {loadingSlots ? 'Creando...' : 'Generar agenda'}
            </button>
          </div>
        </form>
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-dark-700">Mis espacios</h2>
        </div>
        {loadingSlots ? (
          <div className="flex justify-center py-10">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600" />
          </div>
        ) : slots.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {slots.map((slot) => (
              <div key={slot.id_agenda} className="border border-gray-100 rounded-2xl p-4 flex items-center justify-between">
                <div>
                  <p className="font-semibold text-dark-700">{slot.fecha}</p>
                  <p className="text-sm text-dark-500 flex items-center">
                    <Clock className="w-4 h-4 mr-1" />
                    {slot.hora}
                  </p>
                  <p className={`text-xs font-semibold mt-1 ${slot.disponible ? 'text-green-600' : 'text-red-500'}`}>
                    {slot.disponible ? 'Disponible' : 'No disponible'}
                  </p>
                </div>
                <button
                  type="button"
                  className={`btn ${slot.disponible ? 'btn-secondary' : 'btn-primary'}`}
                  onClick={() => toggleSlot(slot)}
                >
                  {slot.disponible ? 'Bloquear' : 'Habilitar'}
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-dark-400">Aún no tienes horarios registrados.</p>
        )}
      </div>
    </div>
  );
};

export default AgendaMedico;

