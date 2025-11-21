import React, { useEffect, useState } from 'react';
import { medicoService } from '../services/api';
import { Stethoscope, User, CheckCircle, XCircle, Clock } from 'lucide-react';

const Medicos = () => {
  const [medicos, setMedicos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterEstado, setFilterEstado] = useState('todos');

  useEffect(() => {
    loadMedicos();
  }, [filterEstado]);

  const loadMedicos = async () => {
    try {
      setLoading(true);
      let data;
      if (filterEstado === 'todos') {
        data = await medicoService.getAll();
      } else {
        data = await medicoService.getByEstado(filterEstado);
      }
      setMedicos(data);
    } catch (error) {
      console.error('Error al cargar médicos:', error);
    } finally {
      setLoading(false);
    }
  };

  const getEstadoIcon = (estado) => {
    switch (estado) {
      case 'Activo':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'Inactivo':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getEstadoColor = (estado) => {
    switch (estado) {
      case 'Activo':
        return 'bg-green-100 text-green-800';
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
          <p className="text-gray-600">Lista de médicos del sistema</p>
        </div>
        <div className="flex items-center space-x-3">
          <label className="text-sm font-medium text-gray-700">Filtrar por:</label>
          <select
            value={filterEstado}
            onChange={(e) => setFilterEstado(e.target.value)}
            className="input w-auto"
          >
            <option value="todos">Todos</option>
            <option value="Activo">Activos</option>
            <option value="Inactivo">Inactivos</option>
          </select>
        </div>
      </div>

      {/* Lista de Médicos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {medicos.length > 0 ? (
          medicos.map((medico) => (
            <div key={medico.id_medico} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                    <Stethoscope className="w-6 h-6 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900">
                      {medico.nombre || `Médico #${medico.id_medico}`}
                    </h3>
                    <p className="text-sm text-gray-600">
                      ID: {medico.id_medico}
                    </p>
                  </div>
                </div>
                <div>{getEstadoIcon(medico.estado)}</div>
              </div>

              <div className="space-y-2 text-sm">
                {medico.especialidad && (
                  <p>
                    <span className="font-medium text-gray-700">Especialidad:</span>{' '}
                    <span className="text-gray-600">{medico.especialidad}</span>
                  </p>
                )}
                {medico.numero_licencia && (
                  <p>
                    <span className="font-medium text-gray-700">Licencia:</span>{' '}
                    <span className="text-gray-600">{medico.numero_licencia}</span>
                  </p>
                )}
                {medico.años_experiencia && (
                  <p>
                    <span className="font-medium text-gray-700">Experiencia:</span>{' '}
                    <span className="text-gray-600">
                      {medico.años_experiencia} años
                    </span>
                  </p>
                )}
                <div className="pt-2">
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded-full ${getEstadoColor(
                      medico.estado
                    )}`}
                  >
                    {medico.estado || 'Pendiente'}
                  </span>
                </div>
              </div>
            </div>
          ))
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
    </div>
  );
};

export default Medicos;
