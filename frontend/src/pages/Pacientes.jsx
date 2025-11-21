import React, { useEffect, useState } from 'react';
import { pacienteService } from '../services/api';
import { Users, Plus, Edit, Trash2, User } from 'lucide-react';

const Pacientes = () => {
  const [pacientes, setPacientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    id_usuario: '',
    grupo_sanguineo: '',
    seguro_medico: '',
    contacto_emergencia: '',
    telefono_emergencia: '',
  });

  useEffect(() => {
    loadPacientes();
  }, []);

  const loadPacientes = async () => {
    try {
      setLoading(true);
      const data = await pacienteService.getAll();
      setPacientes(data);
    } catch (error) {
      console.error('Error al cargar pacientes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await pacienteService.update(editingId, formData);
      } else {
        await pacienteService.create(formData);
      }
      setShowModal(false);
      setEditingId(null);
      setFormData({
        id_usuario: '',
        grupo_sanguineo: '',
        seguro_medico: '',
        contacto_emergencia: '',
        telefono_emergencia: '',
      });
      loadPacientes();
    } catch (error) {
      console.error('Error al guardar paciente:', error);
      alert('Error al guardar el paciente. Por favor, intenta nuevamente.');
    }
  };

  const handleEdit = (paciente) => {
    setEditingId(paciente.id_paciente);
    setFormData({
      id_usuario: paciente.id_usuario || '',
      grupo_sanguineo: paciente.grupo_sanguineo || '',
      seguro_medico: paciente.seguro_medico || '',
      contacto_emergencia: paciente.contacto_emergencia || '',
      telefono_emergencia: paciente.telefono_emergencia || '',
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('¿Estás seguro de eliminar este paciente?')) {
      try {
        await pacienteService.delete(id);
        loadPacientes();
      } catch (error) {
        console.error('Error al eliminar paciente:', error);
        alert('Error al eliminar el paciente.');
      }
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Pacientes</h1>
          <p className="text-gray-600">Gestiona la información de los pacientes</p>
        </div>
        <button
          onClick={() => {
            setEditingId(null);
            setFormData({
              id_usuario: '',
              grupo_sanguineo: '',
              seguro_medico: '',
              contacto_emergencia: '',
              telefono_emergencia: '',
            });
            setShowModal(true);
          }}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>Nuevo Paciente</span>
        </button>
      </div>

      {/* Lista de Pacientes */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {pacientes.length > 0 ? (
          pacientes.map((paciente) => (
            <div key={paciente.id_paciente} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                    <User className="w-6 h-6 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900">
                      Paciente #{paciente.id_paciente}
                    </h3>
                    <p className="text-sm text-gray-600">
                      Usuario ID: {paciente.id_usuario}
                    </p>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEdit(paciente)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Editar"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(paciente.id_paciente)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Eliminar"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="space-y-2 text-sm">
                {paciente.grupo_sanguineo && (
                  <p>
                    <span className="font-medium text-gray-700">Grupo Sanguíneo:</span>{' '}
                    <span className="text-gray-600">{paciente.grupo_sanguineo}</span>
                  </p>
                )}
                {paciente.seguro_medico && (
                  <p>
                    <span className="font-medium text-gray-700">Seguro Médico:</span>{' '}
                    <span className="text-gray-600">{paciente.seguro_medico}</span>
                  </p>
                )}
                {paciente.contacto_emergencia && (
                  <p>
                    <span className="font-medium text-gray-700">Contacto Emergencia:</span>{' '}
                    <span className="text-gray-600">{paciente.contacto_emergencia}</span>
                  </p>
                )}
                {paciente.telefono_emergencia && (
                  <p>
                    <span className="font-medium text-gray-700">Teléfono:</span>{' '}
                    <span className="text-gray-600">{paciente.telefono_emergencia}</span>
                  </p>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-full text-center py-12">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">No hay pacientes registrados</p>
          </div>
        )}
      </div>

      {/* Modal para Crear/Editar Paciente */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              {editingId ? 'Editar Paciente' : 'Nuevo Paciente'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  ID Usuario
                </label>
                <input
                  type="number"
                  value={formData.id_usuario}
                  onChange={(e) =>
                    setFormData({ ...formData, id_usuario: e.target.value })
                  }
                  className="input"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Grupo Sanguíneo
                </label>
                <input
                  type="text"
                  value={formData.grupo_sanguineo}
                  onChange={(e) =>
                    setFormData({ ...formData, grupo_sanguineo: e.target.value })
                  }
                  className="input"
                  placeholder="Ej: O+, A-, etc."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Seguro Médico
                </label>
                <input
                  type="text"
                  value={formData.seguro_medico}
                  onChange={(e) =>
                    setFormData({ ...formData, seguro_medico: e.target.value })
                  }
                  className="input"
                  placeholder="Nombre del seguro"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contacto de Emergencia
                </label>
                <input
                  type="text"
                  value={formData.contacto_emergencia}
                  onChange={(e) =>
                    setFormData({ ...formData, contacto_emergencia: e.target.value })
                  }
                  className="input"
                  placeholder="Nombre del contacto"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Teléfono de Emergencia
                </label>
                <input
                  type="text"
                  value={formData.telefono_emergencia}
                  onChange={(e) =>
                    setFormData({ ...formData, telefono_emergencia: e.target.value })
                  }
                  className="input"
                  placeholder="Teléfono"
                />
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setEditingId(null);
                  }}
                  className="btn btn-secondary flex-1"
                >
                  Cancelar
                </button>
                <button type="submit" className="btn btn-primary flex-1">
                  {editingId ? 'Actualizar' : 'Crear'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Pacientes;
