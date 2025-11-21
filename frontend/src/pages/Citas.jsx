import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { citaService, pacienteService, medicoService, agendaService } from '../services/api';
import { Calendar, Plus, X, CheckCircle, Clock } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const Citas = () => {
  const { user } = useAuth();
  const [citas, setCitas] = useState([]);
  const [pacientes, setPacientes] = useState([]);
  const [medicos, setMedicos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    id_paciente: '',
    id_medico: '',
    id_agenda: '',
    fecha: '',
    hora: '',
    motivo: '',
  });

  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Cargar citas según el rol del usuario
      let citasData = [];
      
      if (user?.rol === 'Paciente' && user?.id_usuario) {
        try {
          citasData = await citaService.getByPaciente(user.id_usuario);
        } catch (err) {
          console.warn('Error al cargar citas del paciente:', err);
          citasData = [];
        }
      } else if (user?.rol === 'Medico' && user?.id_usuario) {
        try {
          citasData = await citaService.getByMedico(user.id_usuario);
        } catch (err) {
          console.warn('Error al cargar citas del médico:', err);
          citasData = [];
        }
      } else {
        // Administrador o usuario sin rol específico - no hay endpoint para todas las citas
        citasData = [];
      }
      
      // Cargar pacientes y médicos solo si el usuario tiene permisos
      // Pacientes solo pueden cargarse si es admin
      // Médicos pueden cargarse por todos
      let pacientesData = [];
      if (user?.rol === 'Administrador') {
        try {
          pacientesData = await pacienteService.getAll();
          pacientesData = Array.isArray(pacientesData) ? pacientesData : [];
        } catch (err) {
          console.warn('Error al cargar pacientes:', err);
          pacientesData = [];
        }
      }
      
      let medicosData = [];
      try {
        medicosData = await medicoService.getAll();
        medicosData = Array.isArray(medicosData) ? medicosData : [];
      } catch (err) {
        console.warn('Error al cargar médicos:', err);
        medicosData = [];
      }

      setCitas(Array.isArray(citasData) ? citasData : []);
      setPacientes(Array.isArray(pacientesData) ? pacientesData : []);
      setMedicos(Array.isArray(medicosData) ? medicosData : []);
    } catch (error) {
      console.error('Error al cargar datos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await citaService.create(formData);
      setShowModal(false);
      setFormData({
        id_paciente: '',
        id_medico: '',
        id_agenda: '',
        fecha: '',
        hora: '',
        motivo: '',
      });
      loadData();
    } catch (error) {
      console.error('Error al crear cita:', error);
      alert('Error al crear la cita. Por favor, intenta nuevamente.');
    }
  };

  const handleCancelar = async (id) => {
    if (window.confirm('¿Estás seguro de cancelar esta cita?')) {
      try {
        await citaService.cancelar(id);
        loadData();
      } catch (error) {
        console.error('Error al cancelar cita:', error);
        alert('Error al cancelar la cita.');
      }
    }
  };

  const handleCompletar = async (id) => {
    try {
      await citaService.completar(id);
      loadData();
    } catch (error) {
      console.error('Error al completar cita:', error);
      alert('Error al completar la cita.');
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
        <button
          onClick={() => setShowModal(true)}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>Nueva Cita</span>
        </button>
      </div>

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
              citas.map((cita) => (
                <tr key={cita.id_cita} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {cita.paciente_nombre || `Paciente #${cita.id_paciente}`}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {cita.medico_nombre || `Médico #${cita.id_medico}`}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {cita.fecha
                      ? format(new Date(cita.fecha), 'dd MMM yyyy', {
                          locale: es,
                        })
                      : '-'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {cita.hora || '-'}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${getEstadoColor(
                        cita.estado
                      )}`}
                    >
                      {cita.estado || 'Pendiente'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center space-x-2">
                      {cita.estado === 'Programada' && (
                        <>
                          <button
                            onClick={() => handleCompletar(cita.id_cita)}
                            className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                            title="Completar"
                          >
                            <CheckCircle className="w-5 h-5" />
                          </button>
                          <button
                            onClick={() => handleCancelar(cita.id_cita)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Cancelar"
                          >
                            <X className="w-5 h-5" />
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))
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
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Paciente
                </label>
                <select
                  value={formData.id_paciente}
                  onChange={(e) =>
                    setFormData({ ...formData, id_paciente: e.target.value })
                  }
                  className="input"
                  required
                >
                  <option value="">Selecciona un paciente</option>
                  {pacientes.map((paciente) => (
                    <option key={paciente.id_paciente} value={paciente.id_paciente}>
                      {paciente.nombre || `Paciente #${paciente.id_paciente}`}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Médico
                </label>
                <select
                  value={formData.id_medico}
                  onChange={(e) =>
                    setFormData({ ...formData, id_medico: e.target.value })
                  }
                  className="input"
                  required
                >
                  <option value="">Selecciona un médico</option>
                  {medicos.map((medico) => (
                    <option key={medico.id_medico} value={medico.id_medico}>
                      {medico.nombre || `Médico #${medico.id_medico}`}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fecha
                </label>
                <input
                  type="date"
                  value={formData.fecha}
                  onChange={(e) =>
                    setFormData({ ...formData, fecha: e.target.value })
                  }
                  className="input"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Hora
                </label>
                <input
                  type="time"
                  value={formData.hora}
                  onChange={(e) =>
                    setFormData({ ...formData, hora: e.target.value })
                  }
                  className="input"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Motivo
                </label>
                <textarea
                  value={formData.motivo}
                  onChange={(e) =>
                    setFormData({ ...formData, motivo: e.target.value })
                  }
                  className="input"
                  rows="3"
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
