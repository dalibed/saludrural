import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, Clock, Loader2, ShieldCheck } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { agendaService, citaService } from '../services/api';

const getIdUsuarioMedico = (doctor) =>
  doctor?.id_usuario || doctor?.ID_Usuario || doctor?.id_usuario_medico || doctor?.ID_Usuario_Medico;

const BookAppointmentModal = ({ doctor, onClose, onSuccess }) => {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const [slots, setSlots] = useState([]);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [reason, setReason] = useState('');
  const [status, setStatus] = useState({ type: '', message: '' });
  const medicoUsuarioId = getIdUsuarioMedico(doctor);

  useEffect(() => {
    if (!doctor || !isAuthenticated || user?.rol !== 'Paciente') return;
    const loadSlots = async () => {
      try {
        setLoadingSlots(true);
        const data = await agendaService.getDisponiblesByMedico(medicoUsuarioId);
        // El endpoint getDisponiblesByMedico ya devuelve solo los slots disponibles
        // No necesitamos filtrar adicionalmente, solo asegurarnos de que sea un array
        const slotsDisponibles = Array.isArray(data) ? data : [];
        
        console.log('Slots disponibles recibidos del backend:', slotsDisponibles.length);
        console.log('Datos recibidos:', data);
        setSlots(slotsDisponibles);
      } catch (error) {
        console.error('Error al cargar disponibilidad', error);
        setStatus({
          type: 'error',
          message:
            error.response?.data?.detail ||
            'No pudimos obtener la agenda del médico. Intenta nuevamente más tarde.',
        });
      } finally {
        setLoadingSlots(false);
      }
    };
    loadSlots();
  }, [doctor, isAuthenticated, user, medicoUsuarioId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedSlot || !user) return;

    try {
      await citaService.create({
        id_usuario_paciente: user.id_usuario,
        id_usuario_medico: medicoUsuarioId,
        id_agenda: selectedSlot.id_agenda,
        motivo_consulta: reason,
      });
      setStatus({
        type: 'success',
        message: 'Tu cita fue agendada correctamente. Recibirás un correo con los detalles.',
      });
      setReason('');
      setSelectedSlot(null);
      onSuccess?.();
    } catch (error) {
      console.error('Error al agendar cita', error);
      const errorMessage = error.response?.data?.detail || 'No se pudo agendar la cita. Verifica la información e inténtalo nuevamente.';
      
      // Si el horario ya no está disponible, recargar los slots disponibles
      if (errorMessage.includes('ya no está disponible') || errorMessage.includes('no está disponible')) {
        setStatus({
          type: 'error',
          message: 'Este horario ya no está disponible. Por favor, selecciona otro horario.',
        });
        setSelectedSlot(null);
        // Recargar slots disponibles
        try {
          const data = await agendaService.getDisponiblesByMedico(medicoUsuarioId);
          // El endpoint ya devuelve solo los disponibles
          const slotsDisponibles = Array.isArray(data) ? data : [];
          setSlots(slotsDisponibles);
        } catch (reloadError) {
          console.error('Error al recargar slots', reloadError);
        }
      } else {
        setStatus({
          type: 'error',
          message: errorMessage,
        });
      }
    }
  };

  const renderContent = () => {
    if (!isAuthenticated) {
      return (
        <div className="text-center space-y-4 py-6">
          <ShieldCheck className="w-12 h-12 text-primary-500 mx-auto" />
          <p className="text-lg font-semibold text-dark-700">Necesitas iniciar sesión</p>
          <p className="text-sm text-dark-400">
            Para reservar una cita debes registrarte o ingresar a la plataforma.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 mt-4">
            <button className="btn btn-secondary flex-1" onClick={() => navigate('/login')}>
              Ingresar
            </button>
          </div>
        </div>
      );
    }

    if (user?.rol !== 'Paciente') {
      return (
        <div className="text-center space-y-4 py-6">
          <ShieldCheck className="w-12 h-12 text-primary-500 mx-auto" />
          <p className="text-lg font-semibold text-dark-700">
            Solo los pacientes pueden agendar citas
          </p>
          <p className="text-sm text-dark-400">
            Ingresa con una cuenta de paciente para completar el proceso.
          </p>
        </div>
      );
    }

    return (
      <form className="space-y-5" onSubmit={handleSubmit}>
        <div>
          <p className="text-sm font-semibold text-dark-500 mb-3">1. Selecciona una franja</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-48 overflow-y-auto pr-1">
            {loadingSlots && (
              <div className="col-span-2 flex justify-center py-6">
                <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
              </div>
            )}
            {!loadingSlots && slots.length === 0 && (
              <p className="text-sm text-dark-400 col-span-2">
                El médico no tiene cupos disponibles. Intenta más tarde.
              </p>
            )}
            {slots.map((slot) => (
              <button
                type="button"
                key={slot.id_agenda}
                onClick={() => setSelectedSlot(slot)}
                className={`p-3 rounded-2xl border text-left transition-all ${
                  selectedSlot?.id_agenda === slot.id_agenda
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-gray-200 hover:border-primary-200'
                }`}
              >
                <div className="flex items-center text-sm font-semibold">
                  <Calendar className="w-4 h-4 mr-2" />
                  {slot.fecha}
                </div>
                <div className="flex items-center text-xs text-dark-400 mt-1">
                  <Clock className="w-4 h-4 mr-2" />
                  {slot.hora}
                </div>
              </button>
            ))}
          </div>
        </div>

        <div>
          <p className="text-sm font-semibold text-dark-500 mb-2">2. Describe tu motivo</p>
          <textarea
            className="input min-h-28"
            placeholder="Ejemplo: controles de hipertensión, seguimiento..."
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            required
          />
        </div>

        {status.message && (
          <div
            className={`p-3 rounded-2xl text-sm ${
              status.type === 'success'
                ? 'bg-green-50 text-green-800 border border-green-100'
                : 'bg-red-50 text-red-700 border border-red-100'
            }`}
          >
            {status.message}
          </div>
        )}

        <div className="flex flex-col sm:flex-row gap-3 pt-2">
          <button type="button" className="btn btn-secondary flex-1" onClick={onClose}>
            Cancelar
          </button>
          <button
            type="submit"
            className="btn btn-primary flex-1 disabled:opacity-60"
            disabled={!selectedSlot || !reason}
          >
            Confirmar cita
          </button>
        </div>
      </form>
    );
  };

  if (!doctor) return null;

  return (
    <div className="fixed inset-0 bg-dark-900/60 backdrop-blur-sm z-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-3xl shadow-2xl max-w-2xl w-full">
        <div className="flex justify-between items-center px-6 py-4 border-b border-gray-100">
          <div>
            <p className="text-sm text-dark-400">Agendar cita</p>
            <p className="font-semibold text-dark-700">
              {doctor?.nombre || doctor?.Nombre} {doctor?.apellidos || doctor?.Apellidos}
            </p>
          </div>
          <button className="text-dark-400 hover:text-dark-600" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="p-6">{renderContent()}</div>
      </div>
    </div>
  );
};

export default BookAppointmentModal;

