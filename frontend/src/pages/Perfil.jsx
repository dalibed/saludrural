import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { authService, pacienteService, usuarioService, documentoService, tipoDocumentoService } from '../services/api';
import { User, Mail, Phone, Calendar, Lock, Save, ShieldCheck, UploadCloud } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const Perfil = () => {
  const { user, checkAuth } = useAuth();
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [message, setMessage] = useState({ type: '', text: '' });
  const [pacientePerfil, setPacientePerfil] = useState(null);
  const [profileMessage, setProfileMessage] = useState('');
  const [usuarioForm, setUsuarioForm] = useState({
    nombre: user?.nombre || '',
    apellidos: user?.apellidos || '',
    correo: user?.correo || '',
    telefono: user?.telefono || '',
  });
  const [userMessage, setUserMessage] = useState('');
  const [docForm, setDocForm] = useState({
    id_tipo_documento: '',
    archivo: '',
  });
  const [docTypes, setDocTypes] = useState([]);
  const [documentos, setDocumentos] = useState([]);
  const [docMessage, setDocMessage] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    setUsuarioForm({
      nombre: user?.nombre || '',
      apellidos: user?.apellidos || '',
      correo: user?.correo || '',
      telefono: user?.telefono || '',
    });

    const loadPacienteData = async () => {
      if (user?.rol !== 'Paciente') return;
      try {
        const data = await pacienteService.getById(user.id_usuario);
        setPacientePerfil({
          grupo_sanguineo: data?.grupo_sanguineo || '',
          seguro_medico: data?.seguro_medico || '',
          contacto_emergencia: data?.contacto_emergencia || '',
          telefono_emergencia: data?.telefono_emergencia || '',
        });
      } catch (error) {
        console.error('Error al cargar perfil de paciente', error);
      }
    };
    const loadMedicoDocs = async () => {
      if (user?.rol !== 'Medico') return;
      try {
        const [types, docs] = await Promise.all([
          tipoDocumentoService.list().catch(() => []),
          documentoService.listByMedico(user.id_usuario).catch(() => []),
        ]);
        setDocTypes(Array.isArray(types) ? types : []);
        setDocumentos(Array.isArray(docs) ? docs : []);
      } catch (error) {
        console.error('Error al cargar documentos de médico', error);
      }
    };

    loadPacienteData();
    loadMedicoDocs();
  }, [user]);

  const handleChangePassword = async (e) => {
    e.preventDefault();

    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage({
        type: 'error',
        text: 'Las contraseñas no coinciden',
      });
      return;
    }

    if (passwordData.new_password.length < 8) {
      setMessage({
        type: 'error',
        text: 'La contraseña debe tener al menos 8 caracteres',
      });
      return;
    }

    try {
      await authService.changePassword(
        passwordData.old_password,
        passwordData.new_password
      );
      setMessage({
        type: 'success',
        text: 'Contraseña actualizada correctamente',
      });
      setPasswordData({
        old_password: '',
        new_password: '',
        confirm_password: '',
      });
      setShowPasswordForm(false);
    } catch (error) {
      setMessage({
        type: 'error',
        text:
          error.response?.data?.detail ||
          'Error al cambiar la contraseña. Verifica tu contraseña actual.',
      });
    }
  };

  const handleUpdatePaciente = async (e) => {
    e.preventDefault();
    if (!user || user.rol !== 'Paciente' || !pacientePerfil) return;

    try {
      await pacienteService.update(user.id_usuario, pacientePerfil);
      setProfileMessage('Información clínica actualizada correctamente.');
    } catch (error) {
      console.error('Error al actualizar perfil de paciente', error);
      setProfileMessage(
        error.response?.data?.detail || 'No pudimos guardar los cambios. Intenta nuevamente.'
      );
    }
  };

  const handleUpdateUsuario = async (e) => {
    e.preventDefault();
    if (!user) return;
    try {
      await usuarioService.update(user.id_usuario, usuarioForm);
      setUserMessage('Datos personales actualizados.');
      await checkAuth();
    } catch (error) {
      console.error('Error al actualizar usuario', error);
      setUserMessage(error.response?.data?.detail || 'No pudimos actualizar tus datos.');
    }
  };

  const handleFileChange = (file) => {
    if (!file) return;
    setSelectedFile(file);
    // Solo guardamos el nombre del archivo, no el contenido
    setDocForm((prev) => ({ ...prev, archivo: file.name }));
  };

  const handleUploadDocumento = async (e) => {
    e.preventDefault();
    if (!docForm.id_tipo_documento || !docForm.archivo || !selectedFile) {
      setDocMessage('Por favor, selecciona un tipo de documento y un archivo.');
      return;
    }

    // Validar que el usuario esté autenticado
    if (!user || !user.id_usuario) {
      setDocMessage('Error: No estás autenticado. Por favor, inicia sesión nuevamente.');
      return;
    }

    // Verificar que el token esté presente
    const token = localStorage.getItem('access_token');
    if (!token) {
      setDocMessage('Error: No se encontró el token de autenticación. Por favor, inicia sesión nuevamente.');
      return;
    }

    // Validar que id_tipo_documento sea un número válido
    const idTipoDoc = Number(docForm.id_tipo_documento);
    if (isNaN(idTipoDoc) || idTipoDoc <= 0) {
      setDocMessage('Error: Por favor, selecciona un tipo de documento válido.');
      return;
    }

    // Validar que el nombre del archivo no esté vacío
    if (!docForm.archivo || docForm.archivo.trim() === '') {
      setDocMessage('Error: El nombre del archivo no puede estar vacío.');
      return;
    }

    // Preparar los datos a enviar
    const datosEnvio = {
      id_usuario_medico: user.id_usuario,
      id_tipo_documento: idTipoDoc,
      archivo: docForm.archivo.trim(), // Solo el nombre del archivo
    };

    console.log('Enviando datos:', datosEnvio);

    try {
      await documentoService.upload(datosEnvio);
      setDocMessage('Documento enviado para validación.');
      setDocForm({ id_tipo_documento: '', archivo: '' });
      setSelectedFile(null);
      const docs = await documentoService.listByMedico(user.id_usuario);
      setDocumentos(Array.isArray(docs) ? docs : []);
    } catch (error) {
      console.error('Error al subir documento', error);
      console.error('Error response:', error.response);
      console.error('Error data:', error.response?.data);
      
      // Manejar diferentes tipos de errores
      if (error.response?.status === 401) {
        setDocMessage('Error de autenticación. Por favor, inicia sesión nuevamente.');
        // Opcional: redirigir al login
        // window.location.href = '/login';
      } else if (error.response?.status === 403) {
        setDocMessage(error.response?.data?.detail || 'No tienes permiso para realizar esta acción.');
      } else if (error.response?.status === 400) {
        // Mostrar errores específicos del serializer si están disponibles
        const errors = error.response?.data?.errors;
        if (errors) {
          const errorMessages = Object.entries(errors)
            .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
            .join('; ');
          setDocMessage(`Datos inválidos: ${errorMessages}`);
        } else {
          setDocMessage(error.response?.data?.detail || 'Datos inválidos. Verifica la información ingresada.');
        }
      } else {
        setDocMessage(error.response?.data?.detail || 'No pudimos subir el documento. Intenta nuevamente.');
      }
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Mi Perfil</h1>
        <p className="text-gray-600">Gestiona tu información personal</p>
      </div>

      {/* Información del Usuario */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Información Personal
        </h2>
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center">
              <User className="w-10 h-10 text-primary-600" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-900">
                {user?.nombre} {user?.apellidos}
              </h3>
              <p className="text-gray-600">{user?.rol}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            <div className="flex items-start space-x-3">
              <Mail className="w-5 h-5 text-gray-400 mt-1" />
              <div>
                <p className="text-sm font-medium text-gray-700">Correo</p>
                <p className="text-gray-900">{user?.correo || 'No disponible'}</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <Phone className="w-5 h-5 text-gray-400 mt-1" />
              <div>
                <p className="text-sm font-medium text-gray-700">Teléfono</p>
                <p className="text-gray-900">{user?.telefono || 'No disponible'}</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <Calendar className="w-5 h-5 text-gray-400 mt-1" />
              <div>
                <p className="text-sm font-medium text-gray-700">
                  Fecha de Nacimiento
                </p>
                <p className="text-gray-900">
                  {user?.fecha_nacimiento
                    ? format(new Date(user.fecha_nacimiento), 'dd MMM yyyy', {
                        locale: es,
                      })
                    : 'No disponible'}
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <User className="w-5 h-5 text-gray-400 mt-1" />
              <div>
                <p className="text-sm font-medium text-gray-700">Documento</p>
                <p className="text-gray-900">{user?.documento || 'No disponible'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Editar datos personales</h2>
        {userMessage && (
          <div className="mb-4 text-sm text-primary-700 bg-primary-50 rounded-xl px-4 py-2">
            {userMessage}
          </div>
        )}
        <form className="grid grid-cols-1 md:grid-cols-2 gap-4" onSubmit={handleUpdateUsuario}>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Nombre</label>
            <input
              className="input"
              value={usuarioForm.nombre}
              onChange={(e) => setUsuarioForm((prev) => ({ ...prev, nombre: e.target.value }))}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Apellidos</label>
            <input
              className="input"
              value={usuarioForm.apellidos}
              onChange={(e) => setUsuarioForm((prev) => ({ ...prev, apellidos: e.target.value }))}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Correo</label>
            <input
              type="email"
              className="input"
              value={usuarioForm.correo}
              onChange={(e) => setUsuarioForm((prev) => ({ ...prev, correo: e.target.value }))}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Teléfono</label>
            <input
              className="input"
              value={usuarioForm.telefono}
              onChange={(e) => setUsuarioForm((prev) => ({ ...prev, telefono: e.target.value }))}
            />
          </div>
          <div className="md:col-span-2 flex justify-end">
            <button type="submit" className="btn btn-primary">
              Guardar datos
            </button>
          </div>
        </form>
      </div>

      {user?.rol === 'Paciente' && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">Datos clínicos</h2>
            <ShieldCheck className="w-5 h-5 text-primary-600" />
          </div>
          <form className="grid grid-cols-1 md:grid-cols-2 gap-4" onSubmit={handleUpdatePaciente}>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Grupo sanguíneo
              </label>
              <input
                type="text"
                value={pacientePerfil?.grupo_sanguineo || ''}
                onChange={(e) =>
                  setPacientePerfil((prev) => ({ ...prev, grupo_sanguineo: e.target.value }))
                }
                className="input"
                placeholder="O+, A-, etc."
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Seguro médico
              </label>
              <input
                type="text"
                value={pacientePerfil?.seguro_medico || ''}
                onChange={(e) =>
                  setPacientePerfil((prev) => ({ ...prev, seguro_medico: e.target.value }))
                }
                className="input"
                placeholder="Nombre de la EPS"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Contacto de emergencia
              </label>
              <input
                type="text"
                value={pacientePerfil?.contacto_emergencia || ''}
                onChange={(e) =>
                  setPacientePerfil((prev) => ({
                    ...prev,
                    contacto_emergencia: e.target.value,
                  }))
                }
                className="input"
                placeholder="Nombre completo"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Teléfono de emergencia
              </label>
              <input
                type="text"
                value={pacientePerfil?.telefono_emergencia || ''}
                onChange={(e) =>
                  setPacientePerfil((prev) => ({
                    ...prev,
                    telefono_emergencia: e.target.value,
                  }))
                }
                className="input"
                placeholder="+57 300 000 0000"
              />
            </div>
            {profileMessage && (
              <div className="col-span-full text-sm text-primary-600 bg-primary-50 rounded-xl px-4 py-2">
                {profileMessage}
              </div>
            )}
            <div className="col-span-full flex justify-end">
              <button type="submit" className="btn btn-primary" disabled={!pacientePerfil}>
                Guardar cambios
              </button>
            </div>
          </form>
        </div>
      )}

      {user?.rol === 'Medico' && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">Documentos para validación</h2>
          </div>
          {docMessage && (
            <div className="mb-4 text-sm text-primary-700 bg-primary-50 rounded-xl px-4 py-2">
              {docMessage}
            </div>
          )}
          <form className="grid grid-cols-1 md:grid-cols-3 gap-4" onSubmit={handleUploadDocumento}>
            <div className="md:col-span-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">Tipo de documento</label>
              <select
                className="input"
                value={docForm.id_tipo_documento}
                onChange={(e) => setDocForm((prev) => ({ ...prev, id_tipo_documento: e.target.value }))}
                required
              >
                <option value="">Selecciona un tipo</option>
                {docTypes.map((tipo) => (
                  <option key={tipo.ID_TipoDocumento || tipo.id_tipo_documento} value={tipo.ID_TipoDocumento || tipo.id_tipo_documento}>
                    {tipo.Nombre || tipo.nombre}
                  </option>
                ))}
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Archivo (PDF o imagen)</label>
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                className="input"
                onChange={(e) => handleFileChange(e.target.files?.[0])}
                required
              />
              {selectedFile && (
                <p className="text-sm text-gray-500 mt-1">Archivo seleccionado: {selectedFile.name}</p>
              )}
            </div>
            <div className="md:col-span-3 flex justify-end">
              <button type="submit" className="btn btn-primary flex items-center space-x-2">
                <UploadCloud className="w-4 h-4" />
                <span>Subir documento</span>
              </button>
            </div>
          </form>

          <div className="mt-6">
            <h3 className="text-lg font-semibold text-dark-700 mb-2">Historial de documentos</h3>
            {documentos.length === 0 ? (
              <p className="text-sm text-dark-400">Aún no has subido documentos.</p>
            ) : (
              <div className="space-y-3">
                {documentos.map((doc) => (
                  <div
                    key={doc.id_documento}
                    className="border border-gray-100 rounded-2xl p-4 flex flex-col md:flex-row md:items-center md:justify-between"
                  >
                    <div>
                      <p className="font-semibold text-dark-700">{doc.tipo_documento}</p>
                      <p className="text-xs text-dark-400">{doc.archivo}</p>
                      <p className="text-xs text-dark-500 mt-1">
                        Estado: <strong>{doc.estado}</strong>
                      </p>
                    </div>
                    <p className="text-xs text-dark-400 mt-2 md:mt-0">
                      Subido el {doc.fecha_subida ? format(new Date(doc.fecha_subida), 'dd MMM yyyy', { locale: es }) : 'N/A'}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Cambiar Contraseña */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">Seguridad</h2>
          <button
            onClick={() => setShowPasswordForm(!showPasswordForm)}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Lock className="w-4 h-4" />
            <span>Cambiar Contraseña</span>
          </button>
        </div>

        {message.text && (
          <div
            className={`mb-4 p-4 rounded-lg ${
              message.type === 'success'
                ? 'bg-green-50 text-green-800 border border-green-200'
                : 'bg-red-50 text-red-800 border border-red-200'
            }`}
          >
            {message.text}
          </div>
        )}

        {showPasswordForm && (
          <form onSubmit={handleChangePassword} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Contraseña Actual
              </label>
              <input
                type="password"
                value={passwordData.old_password}
                onChange={(e) =>
                  setPasswordData({
                    ...passwordData,
                    old_password: e.target.value,
                  })
                }
                className="input"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nueva Contraseña
              </label>
              <input
                type="password"
                value={passwordData.new_password}
                onChange={(e) =>
                  setPasswordData({
                    ...passwordData,
                    new_password: e.target.value,
                  })
                }
                className="input"
                required
                minLength={8}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Confirmar Nueva Contraseña
              </label>
              <input
                type="password"
                value={passwordData.confirm_password}
                onChange={(e) =>
                  setPasswordData({
                    ...passwordData,
                    confirm_password: e.target.value,
                  })
                }
                className="input"
                required
                minLength={8}
              />
            </div>

            <div className="flex space-x-3 pt-2">
              <button
                type="button"
                onClick={() => {
                  setShowPasswordForm(false);
                  setMessage({ type: '', text: '' });
                }}
                className="btn btn-secondary"
              >
                Cancelar
              </button>
              <button type="submit" className="btn btn-primary flex items-center space-x-2">
                <Save className="w-4 h-4" />
                <span>Guardar</span>
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default Perfil;
