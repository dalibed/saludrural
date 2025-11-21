import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { citaService, pacienteService, medicoService, videollamadaService } from '../services/api';
import { Calendar, Plus, X, CheckCircle, Clock, Video } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const Citas = () => {
  const { user } = useAuth();
  const [citas, setCitas] = useState([]);
  const [pacientes, setPacientes] = useState([]);
  const [medicos, setMedicos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [alert, setAlert] = useState({ type: '', text: '' });
  const [formData, setFormData] = useState({
    id_usuario_paciente: '',
    id_usuario_medico: '',
    id_agenda: '',
    motivo_consulta: '',
  });

  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user]);

  const loadData = async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      
      let citasData = [];
      if (user?.rol === 'Paciente' && user?.id_usuario) {
        try {
          citasData = await citaService.getByPaciente(user.id_usuario);
        } catch (err) {
          console.warn('Error al cargar citas del paciente:', err);
        }
      } else if (user?.rol === 'Medico' && user?.id_usuario) {
        try {
          citasData = await citaService.getByMedico(user.id_usuario);
        } catch (err) {
          console.warn('Error al cargar citas del médico:', err);
        }
      } else if (user?.rol === 'Administrador') {
        citasData = [];
      }

      let pacientesData = [];
      if (user?.rol === 'Administrador') {
        try {
          const response = await pacienteService.getAll();
          pacientesData = Array.isArray(response) ? response : [];
        } catch (err) {
          console.warn('Error al cargar pacientes (solo admin):', err);
        }
      }

      let medicosData = [];
      try {
        const response = await medicoService.getAll();
        medicosData = Array.isArray(response) ? response : [];
      } catch (err) {
        console.warn('Error al cargar médicos:', err);
      }

      setCitas(Array.isArray(citasData) ? citasData : []);
      setPacientes(Array.isArray(pacientesData) ? pacientesData : []);
      setMedicos(Array.isArray(medicosData) ? medicosData : []);
    } catch (error) {
      console.error('Error al cargar datos:', error);
      setAlert({
        type: 'error',
        text: 'Error al cargar las citas. Por favor, intenta nuevamente.',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!user) return;
    
    try {
      // Si es paciente, usar su propio ID
      const dataToSend = {
        ...formData,
        id_usuario_paciente: user.rol === 'Paciente' ? user.id_usuario : formData.id_usuario_paciente,
      };
      
      await citaService.create(dataToSend);
      setShowModal(false);
      setFormData({
        id_usuario_paciente: '',
        id_usuario_medico: '',
        id_agenda: '',
        motivo_consulta: '',
      });
      setAlert({
        type: 'success',
        text: 'Tu cita fue creada exitosamente.',
      });
      loadData();
    } catch (error) {
      console.error('Error al crear cita:', error);
      const errorMessage = error.response?.data?.detail || 'Error al crear la cita. Por favor, intenta nuevamente.';
      setAlert({ type: 'error', text: errorMessage });
    }
  };

  const handleCancelar = async (id) => {
    if (!user) return;
    
    if (window.confirm('¿Estás seguro de cancelar esta cita?')) {
      try {
        await citaService.cancelar(id, {
          id_usuario: user.id_usuario,
          motivo_cancelacion: 'Cancelado por el usuario',
        });
        loadData();
      } catch (error) {
        console.error('Error al cancelar cita:', error);
        const errorMessage = error.response?.data?.detail || 'Error al cancelar la cita.';
        setAlert({ type: 'error', text: errorMessage });
      }
    }
  };

  const handleCompletar = async (id) => {
    if (!user) return;
    
    try {
      await citaService.completar(id, {
        id_usuario_medico: user.id_usuario,
      });
      setAlert({
        type: 'success',
        text: 'La cita se marcó como atendida.',
      });
      loadData();
    } catch (error) {
      console.error('Error al completar cita:', error);
      const errorMessage = error.response?.data?.detail || 'Error al completar la cita.';
      setAlert({ type: 'error', text: errorMessage });
    }
  };

  const handleVerVideollamada = async (id) => {
    try {
      const data = await videollamadaService.getByCita(id);
      const enlace = data?.enlace || data?.Enlace;
      if (enlace) {
        window.open(enlace, '_blank', 'noopener');
      } else {
        alert('El médico aún no configura un enlace de videollamada para esta cita.');
      }
    } catch (error) {
      console.error('Error al obtener videollamada:', error);
      const errorMessage =
        error.response?.data?.detail ||
        'No pudimos recuperar el enlace de la videollamada. Intenta nuevamente.';
      alert(errorMessage);
    }
  };

  const handleConfigurarVideollamada = async (id) => {
    const enlace = window.prompt('Ingresa el enlace de la videollamada (Zoom, Meet, etc.)');
    if (!enlace) return;

    try {
      await videollamadaService.crear(id, { enlace });
      alert('Videollamada configurada correctamente.');
    } catch (error) {
      console.error('Error al configurar videollamada:', error);
      const errorMessage =
        error.response?.data?.detail ||
        'No pudimos guardar el enlace. Verifica que seas el médico de la cita.';
      alert(errorMessage);
    }
  };

  const getEstadoColor = (estado) => {
    switch (estado) {
      case 'Programada':
        return 'bg-blue-100 text-blue-800';
      case 'Completada':
        return 'bg-green-100 text-green-800';
      case 'Cancelada':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Citas</h1>
          <p className="text-gray-600">Gestiona todas las citas médicas</p>
        </div>
        {user?.rol === 'Paciente' && (
          <button
            onClick={() => setShowModal(true)}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Plus className="w-5 h-5" />
            <span>Nueva Cita</span>
          </button>
        )}
      </div>

      {alert.text && (
        <div
          className={`rounded-2xl px-4 py-3 text-sm font-medium ${
            alert.type === 'success'
              ? 'bg-green-50 text-green-700 border border-green-200'
              : 'bg-red-50 text-red-700 border border-red-200'
          }`}
        >
          {alert.text}
        </div>
      )}

      {/* Tabla de Citas */}
      <div className="card overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                Paciente
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                Médico
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                Fecha
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                Hora
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                Estado
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {citas.length > 0 ? (
              citas.map((cita) => {
                // Manejar diferentes nombres de campos que pueden venir del stored procedure
                const idCita = cita.id_cita || cita.ID_Cita;
                const pacienteNombre = cita.paciente_nombre || cita.PacienteNombre || cita.nombre_paciente || `Paciente #${cita.id_paciente || cita.ID_Paciente || 'N/A'}`;
                const medicoNombre = cita.medico_nombre || cita.MedicoNombre || cita.nombre_medico || `Médico #${cita.id_medico || cita.ID_Medico || 'N/A'}`;
                const fecha = cita.fecha || cita.Fecha;
                const hora = cita.hora || cita.Hora;
                const estado = cita.estado || cita.Estado || 'Pendiente';
                const motivo = cita.motivo_consulta || cita.MotivoConsulta || '';
                
                return (
                  <tr key={idCita} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">
                      <div className="flex flex-col">
                        <span className="font-medium text-dark-700">{pacienteNombre}</span>
                        {motivo && <span className="text-xs text-dark-400">Motivo: {motivo}</span>}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {medicoNombre}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {fecha
                        ? format(new Date(fecha), 'dd MMM yyyy', {
                            locale: es,
                          })
                        : '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {hora ? (typeof hora === 'string' ? hora : hora.toString().substring(0, 5)) : '-'}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${getEstadoColor(
                          estado
                        )}`}
                      >
                        {estado}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center space-x-2">
                        {estado === 'Programada' && user?.rol === 'Paciente' && (
                          <button
                            onClick={() => handleVerVideollamada(idCita)}
                            className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                            title="Ver videollamada"
                          >
                            <Video className="w-5 h-5" />
                          </button>
                        )}
                        {estado === 'Programada' && user?.rol === 'Medico' && (
                          <button
                            onClick={() => handleConfigurarVideollamada(idCita)}
                            className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                            title="Configurar videollamada"
                          >
                            <Video className="w-5 h-5" />
                          </button>
                        )}
                        {estado === 'Programada' && user?.rol === 'Medico' && (
                          <button
                            onClick={() => handleCompletar(idCita)}
                            className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                            title="Marcar como atendida"
                          >
                            <CheckCircle className="w-5 h-5" />
                          </button>
                        )}
                        {estado === 'Programada' &&
                          (user?.rol === 'Paciente' || user?.rol === 'Medico' || user?.rol === 'Administrador') && (
                            <button
                              onClick={() => handleCancelar(idCita)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                              title="Cancelar"
                            >
                              <X className="w-5 h-5" />
                            </button>
                          )}
                      </div>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                  No hay citas registradas
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Modal para Nueva Cita */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Nueva Cita
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              {user?.rol === 'Administrador' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Paciente
                  </label>
                  <select
                    value={formData.id_usuario_paciente}
                    onChange={(e) =>
                      setFormData({ ...formData, id_usuario_paciente: e.target.value })
                    }
                    className="input"
                    required
                  >
                    <option value="">Selecciona un paciente</option>
                    {pacientes.map((paciente) => (
                      <option key={paciente.id_paciente} value={paciente.id_usuario?.id_usuario || paciente.id_usuario}>
                        {paciente.id_usuario?.nombre || `Paciente #${paciente.id_paciente}`}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Médico
                </label>
                <select
                  value={formData.id_usuario_medico}
                  onChange={(e) =>
                    setFormData({ ...formData, id_usuario_medico: e.target.value })
                  }
                  className="input"
                  required
                >
                  <option value="">Selecciona un médico</option>
                  {medicos.map((medico) => (
                    <option key={medico.id_medico} value={medico.id_usuario?.id_usuario || medico.id_usuario}>
                      {medico.id_usuario?.nombre || `Médico #${medico.id_medico}`}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  ID de Agenda
                </label>
                <input
                  type="number"
                  value={formData.id_agenda}
                  onChange={(e) =>
                    setFormData({ ...formData, id_agenda: e.target.value })
                  }
                  className="input"
                  required
                  placeholder="ID del bloque de agenda"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Motivo de Consulta
                </label>
                <textarea
                  value={formData.motivo_consulta}
                  onChange={(e) =>
                    setFormData({ ...formData, motivo_consulta: e.target.value })
                  }
                  className="input"
                  rows="3"
                  required
                  placeholder="Describe el motivo de la consulta"
                ></textarea>
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="btn btn-secondary flex-1"
                >
                  Cancelar
                </button>
                <button type="submit" className="btn btn-primary flex-1">
                  Crear Cita
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Citas;
