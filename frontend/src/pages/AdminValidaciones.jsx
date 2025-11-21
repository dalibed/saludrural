import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  especialidadService,
  tipoDocumentoService,
  medicoService,
  documentoService,
} from '../services/api';
import { normalizeDoctor } from '../utils/doctor';
import { CheckCircle, XCircle, Plus } from 'lucide-react';

const AdminValidaciones = () => {
  const { user } = useAuth();
  const isAdmin = user?.rol === 'Administrador';

  const [especialidades, setEspecialidades] = useState([]);
  const [tipoDocumentos, setTipoDocumentos] = useState([]);
  const [medicos, setMedicos] = useState([]);
  const [selectedMedico, setSelectedMedico] = useState(null);
  const [documentos, setDocumentos] = useState([]);
  const [especialidadForm, setEspecialidadForm] = useState({ nombre: '', descripcion: '' });
  const [tipoDocForm, setTipoDocForm] = useState({ nombre: '', descripcion: '' });
  const [observacion, setObservacion] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (isAdmin) {
      loadData();
    }
  }, [isAdmin]);

  const loadData = async () => {
    try {
      const [esp, tipos, medics] = await Promise.all([
        especialidadService.list().catch(() => []),
        tipoDocumentoService.list().catch(() => []),
        medicoService.getAll().catch(() => []),
      ]);
      setEspecialidades(Array.isArray(esp) ? esp : []);
      setTipoDocumentos(Array.isArray(tipos) ? tipos : []);
      setMedicos(Array.isArray(medics) ? medics.map(normalizeDoctor) : []);
    } catch (error) {
      console.error('Error cargando datos de validación', error);
    }
  };

  const loadDocumentos = async (medico) => {
    setSelectedMedico(medico);
    setDocumentos([]);
    try {
      const data = await documentoService.listByMedico(medico.usuarioId || medico.id_usuario);
      setDocumentos(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error al cargar documentos del médico', error);
    }
  };

  const handleCreateEspecialidad = async (e) => {
    e.preventDefault();
    setMessage('');
    try {
      await especialidadService.create(especialidadForm);
      setEspecialidadForm({ nombre: '', descripcion: '' });
      setMessage('Especialidad creada correctamente.');
      loadData();
    } catch (error) {
      console.error('Error creando especialidad', error);
      setMessage('No se pudo crear la especialidad.');
    }
  };

  const handleCreateTipoDocumento = async (e) => {
    e.preventDefault();
    setMessage('');
    try {
      await tipoDocumentoService.create(tipoDocForm);
      setTipoDocForm({ nombre: '', descripcion: '' });
      setMessage('Tipo de documento creado correctamente.');
      loadData();
    } catch (error) {
      console.error('Error creando tipo de documento', error);
      setMessage('No se pudo crear el tipo de documento.');
    }
  };

  const handleValidarDocumento = async (doc, estado) => {
    if (!selectedMedico) return;
    try {
      await documentoService.validate(doc.id_documento, {
        id_usuario_admin: user.id_usuario,
        estado,
        observaciones: observacion || `Documento ${estado.toLowerCase()}.`,
      });
      setObservacion('');
      await loadDocumentos(selectedMedico);
    } catch (error) {
      console.error('Error validando documento', error);
    }
  };

  if (!isAdmin) {
    return <Navigate to="/app/dashboard" replace />;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-dark-800">Validaciones</h1>
          <p className="text-dark-500">Gestiona especialidades, tipos de documento y aprobación</p>
        </div>
      </div>

      {message && (
        <div className="card bg-primary-50 border border-primary-100 text-primary-700 text-sm">
          {message}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-dark-700">Especialidades</h2>
          </div>
          <form className="space-y-3" onSubmit={handleCreateEspecialidad}>
            <input
              className="input"
              placeholder="Nombre"
              value={especialidadForm.nombre}
              onChange={(e) => setEspecialidadForm((prev) => ({ ...prev, nombre: e.target.value }))}
              required
            />
            <textarea
              className="input"
              rows={2}
              placeholder="Descripción"
              value={especialidadForm.descripcion}
              onChange={(e) =>
                setEspecialidadForm((prev) => ({ ...prev, descripcion: e.target.value }))
              }
              required
            />
            <button type="submit" className="btn btn-primary w-full">
              Crear especialidad
            </button>
          </form>
          <ul className="mt-4 space-y-2 max-h-48 overflow-y-auto text-sm">
            {especialidades.map((esp) => (
              <li key={esp.id_especialidad || esp.ID_Especialidad} className="flex items-center justify-between">
                <span>{esp.nombre || esp.Nombre}</span>
                <span className="text-xs text-dark-400">{esp.descripcion || esp.Descripcion}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-dark-700">Tipos de documento</h2>
            <button
              type="button"
              className="btn btn-secondary text-xs"
              onClick={() =>
                setTipoDocForm({
                  nombre: 'Licencia médica',
                  descripcion: 'Documento emitido por Secretaría de Salud',
                })
              }
            >
              <Plus className="w-4 h-4 mr-1" /> Licencia médica
            </button>
          </div>
          <form className="space-y-3" onSubmit={handleCreateTipoDocumento}>
            <input
              className="input"
              placeholder="Nombre"
              value={tipoDocForm.nombre}
              onChange={(e) => setTipoDocForm((prev) => ({ ...prev, nombre: e.target.value }))}
              required
            />
            <textarea
              className="input"
              rows={2}
              placeholder="Descripción"
              value={tipoDocForm.descripcion}
              onChange={(e) =>
                setTipoDocForm((prev) => ({ ...prev, descripcion: e.target.value }))
              }
              required
            />
            <button type="submit" className="btn btn-primary w-full">
              Crear tipo
            </button>
          </form>
          <ul className="mt-4 space-y-2 max-h-48 overflow-y-auto text-sm">
            {tipoDocumentos.map((tipo) => (
              <li key={tipo.ID_TipoDocumento || tipo.id_tipo_documento} className="flex items-center justify-between">
                <span>{tipo.Nombre || tipo.nombre}</span>
                <span className="text-xs text-dark-400">{tipo.Descripcion || tipo.descripcion}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold text-dark-700 mb-4">Médicos registrados</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-dark-400 border-b">
                <th className="py-2">Nombre</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {medicos.map((medico) => (
                <tr key={medico.id}>
                  <td className="py-2">{medico.nombre}</td>
                  <td>
                    <span className="chip">{medico.estadoValidacion || 'Pendiente'}</span>
                  </td>
                  <td>
                    <button
                      className="btn btn-secondary text-xs"
                      onClick={() => loadDocumentos(medico)}
                    >
                      Ver documentos
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {selectedMedico && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-dark-700">
                Documentos de {selectedMedico.nombre}
              </h2>
              <p className="text-xs text-dark-400">
                Selecciona un documento y apruébalo o recházalo
              </p>
            </div>
          </div>

          {documentos.length === 0 ? (
            <p className="text-sm text-dark-400">Este médico aún no ha cargado documentos.</p>
          ) : (
            <div className="space-y-3">
              {documentos.map((doc) => (
                <div key={doc.id_documento} className="border border-gray-100 rounded-2xl p-4 flex flex-col md:flex-row md:items-center md:justify-between">
                  <div>
                    <p className="font-semibold text-dark-700">{doc.tipo_documento}</p>
                    <p className="text-xs text-dark-400">{doc.archivo}</p>
                    <p className="text-xs text-dark-500 mt-1">
                      Estado: <strong>{doc.estado}</strong>
                    </p>
                  </div>
                  <div className="flex items-center space-x-2 mt-3 md:mt-0">
                    <button
                      className="btn btn-secondary text-xs"
                      onClick={() => handleValidarDocumento(doc, 'Rechazado')}
                    >
                      <XCircle className="w-4 h-4 mr-1" />
                      Rechazar
                    </button>
                    <button
                      className="btn btn-primary text-xs"
                      onClick={() => handleValidarDocumento(doc, 'Aprobado')}
                    >
                      <CheckCircle className="w-4 h-4 mr-1" />
                      Aprobar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="mt-4">
            <label className="block text-xs font-semibold text-dark-500 mb-2">
              Observaciones
            </label>
            <textarea
              className="input"
              rows={2}
              value={observacion}
              onChange={(e) => setObservacion(e.target.value)}
              placeholder="Comentarios para el médico"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminValidaciones;

