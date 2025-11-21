import React, { useEffect, useState } from 'react';
import { medicoService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import DoctorCard from '../components/DoctorCard';
import DoctorProfileModal from '../components/DoctorProfileModal';
import BookAppointmentModal from '../components/BookAppointmentModal';
import { normalizeDoctor } from '../utils/doctor';
import { Stethoscope, CheckCircle, XCircle, Clock } from 'lucide-react';

const Medicos = () => {
  const { user } = useAuth();
  const isPaciente = user?.rol === 'Paciente';
  const [medicos, setMedicos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterEstado, setFilterEstado] = useState('todos');
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [bookingDoctor, setBookingDoctor] = useState(null);

  useEffect(() => {
    loadMedicos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterEstado, isPaciente]);

  const loadMedicos = async () => {
    try {
      setLoading(true);
      if (isPaciente) {
        const data = await medicoService.getByEstado('Aprobado');
        setMedicos(Array.isArray(data) ? data.map(normalizeDoctor) : []);
        return;
      }

      let data;
      if (filterEstado === 'todos') {
        data = await medicoService.getAll();
      } else {
        data = await medicoService.getByEstado(filterEstado);
      }
      setMedicos(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error al cargar médicos:', error);
    } finally {
      setLoading(false);
    }
  };

  const getEstadoIcon = (estado) => {
    switch (estado) {
      case 'Aprobado':
      case 'Activo':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'Rechazado':
      case 'Inactivo':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getEstadoColor = (estado) => {
    switch (estado) {
      case 'Aprobado':
      case 'Activo':
        return 'bg-green-100 text-green-800';
      case 'Rechazado':
      case 'Inactivo':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Médicos</h1>
          <p className="text-gray-600">
            {isPaciente ? 'Directorio de médicos validados' : 'Lista de médicos del sistema'}
          </p>
        </div>
        {!isPaciente && (
          <div className="flex items-center space-x-3">
            <label className="text-sm font-medium text-gray-700">Filtrar por validación:</label>
            <select
              value={filterEstado}
              onChange={(e) => setFilterEstado(e.target.value)}
              className="input w-auto"
            >
              <option value="todos">Todos</option>
              <option value="Aprobado">Aprobados</option>
              <option value="Pendiente">Pendientes</option>
              <option value="Rechazado">Rechazados</option>
            </select>
          </div>
        )}
      </div>

      {isPaciente ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {medicos.map((medico) => (
              <DoctorCard
                key={medico.id || medico.usuarioId}
                doctor={medico}
                onViewProfile={setSelectedDoctor}
                onBook={setBookingDoctor}
              />
            ))}
          </div>
          {selectedDoctor && (
            <DoctorProfileModal doctor={selectedDoctor} onClose={() => setSelectedDoctor(null)} />
          )}
          {bookingDoctor && (
            <BookAppointmentModal
              doctor={bookingDoctor}
              onClose={() => setBookingDoctor(null)}
              onSuccess={() => setBookingDoctor(null)}
            />
          )}
        </>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {medicos.length > 0 ? (
            medicos.map((medico) => {
              const normalized = normalizeDoctor(medico);
              const estado = normalized.estadoValidacion || medico.estado || 'Pendiente';
              return (
                <div key={normalized.id} className="card hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                        <Stethoscope className="w-6 h-6 text-primary-600" />
                      </div>
                      <div>
                        <h3 className="font-bold text-gray-900">{normalized.nombre}</h3>
                        <p className="text-sm text-gray-600">ID: {normalized.id}</p>
                      </div>
                    </div>
                    <div>{getEstadoIcon(estado)}</div>
                  </div>

                  <div className="space-y-2 text-sm">
                    {normalized.especialidad && (
                      <p>
                        <span className="font-medium text-gray-700">Especialidad:</span>{' '}
                        <span className="text-gray-600">{normalized.especialidad}</span>
                      </p>
                    )}
                    {medico.licencia && (
                      <p>
                        <span className="font-medium text-gray-700">Licencia:</span>{' '}
                        <span className="text-gray-600">{medico.licencia}</span>
                      </p>
                    )}
                    {medico.anios_experiencia && (
                      <p>
                        <span className="font-medium text-gray-700">Experiencia:</span>{' '}
                        <span className="text-gray-600">{medico.anios_experiencia} años</span>
                      </p>
                    )}
                    <div className="pt-2">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getEstadoColor(estado)}`}>
                        {estado}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="col-span-full text-center py-12">
              <Stethoscope className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">
                No hay médicos registrados
                {filterEstado !== 'todos' && ` con estado "${filterEstado}"`}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Medicos;
