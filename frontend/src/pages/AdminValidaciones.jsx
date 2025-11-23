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
  const [estadoMedico, setEstadoMedico] = useState(null);
  const [loadingValidacion, setLoadingValidacion] = useState(false);

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
    setEstadoMedico(null);
    try {
      const data = await documentoService.listByMedico(medico.usuarioId || medico.id_usuario);
      setDocumentos(Array.isArray(data) ? data : []);
      
      // Actualizar estado del médico desde los datos normalizados
      setEstadoMedico({
        estado: medico.estadoValidacion || 'Pendiente',
        nombre: medico.nombre,
      });
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
    setLoadingValidacion(true);
    setMessage('');
    try {
      const resultado = await documentoService.validate(doc.id_documento, {
        id_usuario_admin: user.id_usuario,
        estado,
        observaciones: observacion || `Documento ${estado.toLowerCase()}.`,
      });
      
      // Actualizar estado del médico con la respuesta del servidor
      if (resultado) {
        setEstadoMedico({
          estado: resultado.estado_medico || estadoMedico?.estado || 'Pendiente',
          tipos_aprobados: resultado.tipos_aprobados || 0,
          tipos_requeridos: resultado.tipos_requeridos || 0,
          mensaje: resultado.mensaje || resultado.detail || '',
        });
        setMessage(resultado.detail || `Documento ${estado.toLowerCase()} correctamente.`);
      }
      
      setObservacion('');
      await loadDocumentos(selectedMedico);
    } catch (error) {
      console.error('Error validando documento', error);
      setMessage(error.response?.data?.detail || 'Error al validar el documento.');
    } finally {
      setLoadingValidacion(false);
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
              {medicos.map((medico) => {
                const estado = medico.estadoValidacion || 'Pendiente';
                const getEstadoColor = (est) => {
                  switch (est) {
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
                
                return (
                  <tr key={medico.id} className={selectedMedico?.id === medico.id ? 'bg-primary-50' : ''}>
                    <td className="py-2 font-medium">{medico.nombre}</td>
                    <td>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getEstadoColor(estado)}`}>
                        {estado}
                      </span>
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
                );
              })}
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
                Revisa y valida los documentos del médico
              </p>
            </div>
            {estadoMedico && (
              <div className="text-right">
                <p className="text-xs text-dark-400 mb-1">Estado del médico:</p>
                <span className={`px-3 py-1 text-sm font-medium rounded-full ${
                  estadoMedico.estado === 'Aprobado' || estadoMedico.estado === 'Activo'
                    ? 'bg-green-100 text-green-800'
                    : estadoMedico.estado === 'Rechazado' || estadoMedico.estado === 'Inactivo'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {estadoMedico.estado}
                </span>
                {estadoMedico.tipos_aprobados !== undefined && estadoMedico.tipos_requeridos !== undefined && (
                  <p className="text-xs text-dark-500 mt-1">
                    Documentos: {estadoMedico.tipos_aprobados}/{estadoMedico.tipos_requeridos} aprobados
                  </p>
                )}
              </div>
            )}
          </div>

          {estadoMedico?.mensaje && (
            <div className={`mb-4 p-3 rounded-lg text-sm ${
              estadoMedico.estado === 'Aprobado' || estadoMedico.estado === 'Activo'
                ? 'bg-green-50 text-green-700 border border-green-200'
                : estadoMedico.estado === 'Rechazado' || estadoMedico.estado === 'Inactivo'
                ? 'bg-red-50 text-red-700 border border-red-200'
                : 'bg-yellow-50 text-yellow-700 border border-yellow-200'
            }`}>
              {estadoMedico.mensaje}
            </div>
          )}

          {documentos.length === 0 ? (
            <p className="text-sm text-dark-400">Este médico aún no ha cargado documentos.</p>
          ) : (
            <div className="space-y-3">
              {documentos.map((doc) => {
                const getEstadoColor = (est) => {
                  switch (est) {
                    case 'Aprobado':
                      return 'bg-green-100 text-green-800';
                    case 'Rechazado':
                      return 'bg-red-100 text-red-800';
                    default:
                      return 'bg-yellow-100 text-yellow-800';
                  }
                };
                
                return (
                  <div key={doc.id_documento} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <p className="font-semibold text-dark-700">{doc.tipo_documento || 'Documento'}</p>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getEstadoColor(doc.estado)}`}>
                            {doc.estado || 'Pendiente'}
                          </span>
                        </div>
                        <p className="text-sm text-dark-500 mb-1">
                          <span className="font-medium">Archivo:</span> {doc.archivo}
                        </p>
                        {doc.descripcion && (
                          <p className="text-xs text-dark-400">{doc.descripcion}</p>
                        )}
                        {doc.fecha_subida && (
                          <p className="text-xs text-dark-400 mt-1">
                            Subido el: {new Date(doc.fecha_subida).toLocaleDateString('es-ES')}
                          </p>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        {doc.estado === 'Pendiente' ? (
                          <>
                            <button
                              className="btn btn-secondary text-xs flex items-center gap-1"
                              onClick={() => handleValidarDocumento(doc, 'Rechazado')}
                              disabled={loadingValidacion}
                            >
                              <XCircle className="w-4 h-4" />
                              Rechazar
                            </button>
                            <button
                              className="btn btn-primary text-xs flex items-center gap-1"
                              onClick={() => handleValidarDocumento(doc, 'Aprobado')}
                              disabled={loadingValidacion}
                            >
                              <CheckCircle className="w-4 h-4" />
                              Aprobar
                            </button>
                          </>
                        ) : (
                          <span className="text-xs text-dark-400 italic">
                            {doc.estado === 'Aprobado' ? '✓ Aprobado' : '✗ Rechazado'}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          <div className="mt-6 border-t pt-4">
            <label className="block text-sm font-semibold text-dark-700 mb-2">
              Observaciones (opcional)
            </label>
            <textarea
              className="input"
              rows={3}
              value={observacion}
              onChange={(e) => setObservacion(e.target.value)}
              placeholder="Agrega comentarios o razones para la validación del documento..."
            />
            <p className="text-xs text-dark-400 mt-1">
              Las observaciones se guardarán junto con la validación del documento.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminValidaciones;

