import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { citaService, pacienteService, medicoService, videollamadaService, historiaEntradaService, usuarioService } from '../services/api';
import { Calendar, Plus, X, CheckCircle, Clock, Video, FileText, Edit, Check } from 'lucide-react';
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
  const [showHistoriaModal, setShowHistoriaModal] = useState(false);
  const [citaSeleccionada, setCitaSeleccionada] = useState(null);
  const [historiaForm, setHistoriaForm] = useState({
    diagnostico: '',
    tratamiento: '',
    notas: '',
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
      // Solo administradores pueden cargar la lista completa de pacientes
      // Los médicos obtendrán los nombres de los pacientes desde los datos de la cita
      if (user?.rol === 'Administrador') {
        try {
          const response = await pacienteService.getAll();
          pacientesData = Array.isArray(response) ? response : [];
        } catch (err) {
          console.warn('Error al cargar pacientes:', err);
        }
      }

      let medicosData = [];
      try {
        // Si es paciente, solo cargar médicos aprobados
        if (user?.rol === 'Paciente') {
          const response = await medicoService.getByEstado('Aprobado');
          medicosData = Array.isArray(response) ? response : [];
        } else {
          // Para médicos y administradores, cargar todos
        const response = await medicoService.getAll();
        medicosData = Array.isArray(response) ? response : [];
        }
      } catch (err) {
        console.error('Error al cargar médicos:', err);
        medicosData = [];
      }

      // Log para depuración - ver qué datos llegan
      if (citasData.length > 0) {
        console.log('Ejemplo de datos de cita recibidos:', citasData[0]);
        console.log('Médicos cargados:', medicosData.length);
        console.log('Pacientes cargados:', pacientesData.length);
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

  const handleAceptar = async (id) => {
    if (!user) {
      setAlert({ type: 'error', text: 'No estás autenticado. Por favor, inicia sesión nuevamente.' });
      return;
    }
    
    // Convertir ID a número si es necesario
    const idCita = id ? Number(id) : null;
    
    if (!idCita || isNaN(idCita)) {
      setAlert({ type: 'error', text: 'ID de cita no válido.' });
      return;
    }
    
    try {
      const response = await citaService.aceptar(idCita, {
        id_usuario_medico: user.id_usuario,
      });
      
      setAlert({
        type: 'success',
        text: response?.detail || 'La cita se aceptó correctamente.',
      });
      loadData();
    } catch (error) {
      console.error('Error al aceptar cita:', error);
      const errorMessage = error.response?.data?.detail || 'Error al aceptar la cita.';
      setAlert({ type: 'error', text: errorMessage });
    }
  };

  const handleCompletar = async (id) => {
    if (!user) {
      setAlert({ type: 'error', text: 'No estás autenticado. Por favor, inicia sesión nuevamente.' });
      return;
    }
    
    // Convertir ID a número si es necesario
    const idCita = id ? Number(id) : null;
    
    if (!idCita || isNaN(idCita)) {
      setAlert({ type: 'error', text: 'ID de cita no válido.' });
      return;
    }
    
    try {
      console.log('Completando cita:', { idCita, id_usuario_medico: user.id_usuario });
      const response = await citaService.completar(idCita, {
        id_usuario_medico: user.id_usuario,
      });
      console.log('Respuesta de completar cita:', response);
      
      setAlert({
        type: 'success',
        text: response?.detail || 'La cita se marcó como atendida correctamente.',
      });
      loadData();
    } catch (error) {
      console.error('Error al completar cita:', error);
      console.error('Error response:', error.response);
      console.error('Error data:', error.response?.data);
      
      // Manejar diferentes tipos de errores
      let errorMessage = 'Error al completar la cita.';
      
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.response?.data?.hint) {
        errorMessage = `${error.response.data.detail || errorMessage}. ${error.response.data.hint}`;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setAlert({ type: 'error', text: errorMessage });
    }
  };

  const handleAbrirHistoriaClinica = (cita) => {
    setCitaSeleccionada(cita);
    setHistoriaForm({
      diagnostico: '',
      tratamiento: '',
      notas: '',
    });
    setShowHistoriaModal(true);
  };

  const handleCrearHistoriaEntrada = async (e) => {
    e.preventDefault();
    if (!citaSeleccionada || !user) return;

    try {
      const idCita = citaSeleccionada.id_cita || citaSeleccionada.ID_Cita;
      await historiaEntradaService.create({
        id_usuario_medico: user.id_usuario,
        id_cita: idCita,
        diagnostico: historiaForm.diagnostico,
        tratamiento: historiaForm.tratamiento,
        notas: historiaForm.notas || '',
      });
      
      setAlert({
        type: 'success',
        text: 'Entrada a la historia clínica creada correctamente.',
      });
      setShowHistoriaModal(false);
      setCitaSeleccionada(null);
      setHistoriaForm({ diagnostico: '', tratamiento: '', notas: '' });
      loadData();
    } catch (error) {
      console.error('Error al crear entrada de historia clínica', error);
      const errorMessage = error.response?.data?.detail || 'Error al crear la entrada.';
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
      case 'Atendida':
        return 'bg-green-100 text-green-800';
      case 'Cancelada':
        return 'bg-red-100 text-red-800';
      case 'Pendiente':
        return 'bg-yellow-100 text-yellow-800';
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
              {user?.rol !== 'Paciente' && (
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                Paciente
              </th>
              )}
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
              citas.map((cita, index) => {
                try {
                // Manejar diferentes nombres de campos que pueden venir del stored procedure
                const idCita = cita.id_cita || cita.ID_Cita || cita.IdCita || cita.ID_Cita;
                // Asegurar que el ID sea un número
                const idCitaNumero = idCita ? Number(idCita) : null;
                const idPacienteCita = cita.id_paciente || cita.ID_Paciente || cita.IdPaciente || cita.id_usuario_paciente || cita.ID_Usuario_Paciente;
                const idMedicoCita = cita.id_medico || cita.ID_Medico || cita.IdMedico || cita.id_usuario_medico || cita.ID_Usuario_Medico;
                
                // Convertir IDs a números para comparación
                const idMedicoCitaNum = idMedicoCita ? Number(idMedicoCita) : null;
                const idPacienteCitaNum = idPacienteCita ? Number(idPacienteCita) : null;
                
                // Buscar nombre del paciente en múltiples formatos desde los datos de la cita
                let pacienteNombre = cita.paciente_nombre || 
                                    cita.PacienteNombre || 
                                    cita.nombre_paciente || 
                                    cita.NombrePaciente ||
                                    cita.nombre_paciente_completo ||
                                    cita.NombrePacienteCompleto;
                
                // Si no encontramos el nombre en la cita, intentar construir desde nombre y apellidos
                if (!pacienteNombre || pacienteNombre === 'N/A' || pacienteNombre.trim() === '') {
                  const nombrePac = cita.paciente_nombre || cita.PacienteNombre || cita.nombre || '';
                  const apellidosPac = cita.paciente_apellidos || cita.PacienteApellidos || cita.apellidos || '';
                  pacienteNombre = `${nombrePac} ${apellidosPac}`.trim() || null;
                }
                
                // Si aún no hay nombre y es administrador, buscar en la lista de pacientes cargados
                if ((!pacienteNombre || pacienteNombre === 'N/A' || pacienteNombre.trim() === '') && user?.rol === 'Administrador') {
                  const pacienteEncontrado = pacientes.find(p => {
                    const idPac = p.id_paciente || p.ID_Paciente || p.id_paciente;
                    const idUsu = p.id_usuario?.id_usuario || p.id_usuario || p.ID_Usuario;
                    const idPacNum = idPac ? Number(idPac) : null;
                    const idUsuNum = idUsu ? Number(idUsu) : null;
                    return (idPacNum && idPacNum === idPacienteCitaNum) || 
                           (idUsuNum && idUsuNum === idPacienteCitaNum) ||
                           (idPac && idPac === idPacienteCita) ||
                           (idUsu && idUsu === idPacienteCita);
                  });
                  
                  if (pacienteEncontrado) {
                    // Intentar obtener nombre desde usuario relacionado
                    const usuarioPac = pacienteEncontrado.id_usuario;
                    if (usuarioPac) {
                      pacienteNombre = `${usuarioPac.nombre || ''} ${usuarioPac.apellidos || ''}`.trim() || 
                                      usuarioPac.nombre || 
                                      `Paciente #${idPacienteCita || 'N/A'}`;
                    } else {
                      pacienteNombre = `Paciente #${idPacienteCita || 'N/A'}`;
                    }
                  } else {
                    pacienteNombre = `Paciente #${idPacienteCita || 'N/A'}`;
                  }
                } else if (!pacienteNombre || pacienteNombre === 'N/A' || pacienteNombre.trim() === '') {
                  pacienteNombre = `Paciente #${idPacienteCita || 'N/A'}`;
                }
                
                // Buscar el nombre del médico en múltiples formatos posibles
                let medicoNombre = cita.medico_nombre || 
                                  cita.MedicoNombre || 
                                  cita.nombre_medico || 
                                  cita.NombreMedico ||
                                  cita.medico ||
                                  cita.Medico ||
                                  cita.nombre ||
                                  cita.Nombre;
                
                // Si no encontramos el nombre, intentar construir desde nombre y apellidos
                if (!medicoNombre || medicoNombre === 'N/A') {
                  const nombre = cita.medico_nombre || cita.MedicoNombre || cita.nombre || cita.Nombre || '';
                  const apellidos = cita.medico_apellidos || cita.MedicoApellidos || cita.apellidos || cita.Apellidos || '';
                  medicoNombre = `${nombre} ${apellidos}`.trim() || null;
                }
                
                // Si aún no hay nombre, buscar en la lista de médicos cargados
                if (!medicoNombre || medicoNombre === 'N/A' || medicoNombre.trim() === '') {
                  // Si el usuario actual es médico y está viendo sus propias citas, usar su nombre
                  if (user?.rol === 'Medico' && (user?.id_usuario === idMedicoCitaNum || user?.id_usuario === idMedicoCita)) {
                    medicoNombre = `${user.nombre || ''} ${user.apellidos || ''}`.trim() || user.nombre || `Médico #${idMedicoCita || 'N/A'}`;
                  } else {
                    // Buscar en la lista de médicos cargados
                    const medicoEncontrado = medicos.find(m => {
                      const idMed = m.id_medico || m.ID_Medico || m.id_medico;
                      const idUsu = m.id_usuario?.id_usuario || 
                                   m.id_usuario || 
                                   m.ID_Usuario || 
                                   m.id_usuario_medico || 
                                   m.ID_Usuario_Medico ||
                                   m.usuarioId;
                      
                      const idMedNum = idMed ? Number(idMed) : null;
                      const idUsuNum = idUsu ? Number(idUsu) : null;
                      
                      return (idMedNum && idMedNum === idMedicoCitaNum) || 
                             (idUsuNum && idUsuNum === idMedicoCitaNum) ||
                             (idMed && idMed === idMedicoCita) ||
                             (idUsu && idUsu === idMedicoCita);
                    });
                    
                    if (medicoEncontrado) {
                      // Usar normalizeDoctor si está disponible, o buscar nombre manualmente
                      const nombre = medicoEncontrado.nombre || medicoEncontrado.Nombre || '';
                      const apellidos = medicoEncontrado.apellidos || medicoEncontrado.Apellidos || '';
                      const nombreCompleto = `${nombre} ${apellidos}`.trim();
                      
                      medicoNombre = nombreCompleto || 
                                    medicoEncontrado.nombre_completo || 
                                    medicoEncontrado.NombreCompleto ||
                                    (medicoEncontrado.raw && (medicoEncontrado.raw.nombre || medicoEncontrado.raw.Nombre)) ||
                                    `Médico #${idMedicoCita || 'N/A'}`;
                    } else {
                      medicoNombre = `Médico #${idMedicoCita || 'N/A'}`;
                    }
                  }
                }
                
                const fecha = cita.fecha || cita.Fecha || cita.FechaCita;
                const hora = cita.hora || cita.Hora || cita.HoraCita;
                const estado = cita.estado || cita.Estado || cita.EstadoCita || 'Pendiente';
                const motivo = cita.motivo_consulta || cita.MotivoConsulta || cita.motivo || '';
                
                return (
                  <tr key={idCita || idCitaNumero} className="hover:bg-gray-50">
                    {user?.rol !== 'Paciente' && (
                    <td className="px-4 py-3 text-sm text-gray-900">
                      <div className="flex flex-col">
                        <span className="font-medium text-dark-700">{pacienteNombre}</span>
                        {motivo && <span className="text-xs text-dark-400">Motivo: {motivo}</span>}
                      </div>
                    </td>
                    )}
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
                      <div className="flex items-center space-x-2 flex-wrap gap-2">
                        {/* Acciones para citas Programadas */}
                        {estado === 'Programada' && user?.rol === 'Paciente' && (
                          <button
                            onClick={() => handleVerVideollamada(idCitaNumero || idCita)}
                            className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                            title="Ver videollamada"
                          >
                            <Video className="w-5 h-5" />
                          </button>
                        )}
                        {estado === 'Programada' && user?.rol === 'Medico' && (
                          <>
                          <button
                              onClick={() => handleConfigurarVideollamada(idCitaNumero || idCita)}
                            className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                            title="Configurar videollamada"
                          >
                            <Video className="w-5 h-5" />
                          </button>
                            <button
                              onClick={() => handleCompletar(idCitaNumero || idCita)}
                              className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                              title="Marcar como atendida"
                            >
                              <CheckCircle className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() => handleCancelar(idCitaNumero || idCita)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                              title="Cancelar cita"
                            >
                              <X className="w-5 h-5" />
                            </button>
                          </>
                        )}
                        
                        {/* Acciones para citas Completadas - Médico puede crear historia clínica */}
                        {(estado === 'Completada' || estado === 'Atendida') && user?.rol === 'Medico' && (
                          <button
                            onClick={() => handleAbrirHistoriaClinica(cita)}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Crear entrada en historia clínica"
                          >
                            <FileText className="w-5 h-5" />
                          </button>
                        )}
                        
                        {/* Acciones para citas Pendientes - Médico puede aceptar, marcar como atendida o cancelar */}
                        {estado === 'Pendiente' && user?.rol === 'Medico' && (
                          <>
                            <button
                              onClick={() => handleAceptar(idCitaNumero || idCita)}
                              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                              title="Aceptar cita"
                            >
                              <Check className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() => handleCompletar(idCitaNumero || idCita)}
                            className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                            title="Marcar como atendida"
                          >
                            <CheckCircle className="w-5 h-5" />
                          </button>
                            <button
                              onClick={() => handleCancelar(idCitaNumero || idCita)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                              title="Cancelar cita"
                            >
                              <X className="w-5 h-5" />
                            </button>
                          </>
                        )}
                        
                        {/* Botón de cancelar para pacientes y administradores */}
                        {(estado === 'Programada' || estado === 'Pendiente') &&
                          (user?.rol === 'Paciente' || user?.rol === 'Administrador') && (
                            <button
                              onClick={() => handleCancelar(idCitaNumero || idCita)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                              title="Cancelar cita"
                            >
                              <X className="w-5 h-5" />
                            </button>
                          )}
                      </div>
                    </td>
                  </tr>
                );
                } catch (error) {
                  console.error('Error procesando cita:', error, cita);
                  return (
                    <tr key={index || 'error'}>
                      <td colSpan={user?.rol === 'Paciente' ? 5 : 6} className="px-4 py-3 text-sm text-red-600">
                        Error al cargar esta cita
                      </td>
                    </tr>
                  );
                }
              })
            ) : (
              <tr>
                <td colSpan={user?.rol === 'Paciente' ? 5 : 6} className="px-4 py-8 text-center text-gray-500">
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
                  {medicos.map((medico) => {
                    // Manejar diferentes formatos de datos del backend
                    const idMedico = medico.id_medico || medico.ID_Medico || medico.id_medico;
                    const idUsuario = medico.id_usuario?.id_usuario || 
                                     medico.id_usuario || 
                                     medico.ID_Usuario || 
                                     medico.id_usuario_medico ||
                                     medico.ID_Usuario_Medico;
                    const nombre = medico.nombre || medico.Nombre || '';
                    const apellidos = medico.apellidos || medico.Apellidos || '';
                    const nombreCompleto = `${nombre} ${apellidos}`.trim() || 
                                          medico.nombre_completo || 
                                          medico.NombreCompleto ||
                                          `Médico #${idMedico || idUsuario || 'N/A'}`;
                    
                    return (
                      <option key={idMedico || idUsuario} value={idUsuario}>
                        {nombreCompleto}
                    </option>
                    );
                  })}
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

      {/* Modal para Crear Entrada en Historia Clínica */}
      {showHistoriaModal && citaSeleccionada && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-gray-900">
                Nueva Entrada en Historia Clínica
              </h2>
              <button
                onClick={() => {
                  setShowHistoriaModal(false);
                  setCitaSeleccionada(null);
                  setHistoriaForm({ diagnostico: '', tratamiento: '', notas: '' });
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {citaSeleccionada && (
              <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Paciente:</span>{' '}
                  {citaSeleccionada.paciente_nombre || 
                   citaSeleccionada.PacienteNombre || 
                   citaSeleccionada.nombre_paciente || 
                   'N/A'}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Fecha de la cita:</span>{' '}
                  {citaSeleccionada.fecha || citaSeleccionada.Fecha
                    ? format(new Date(citaSeleccionada.fecha || citaSeleccionada.Fecha), 'dd MMM yyyy', { locale: es })
                    : 'N/A'}
                </p>
                {citaSeleccionada.motivo_consulta && (
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Motivo:</span> {citaSeleccionada.motivo_consulta}
                  </p>
                )}
              </div>
            )}

            <form onSubmit={handleCrearHistoriaEntrada} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Diagnóstico <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={historiaForm.diagnostico}
                  onChange={(e) =>
                    setHistoriaForm((prev) => ({ ...prev, diagnostico: e.target.value }))
                  }
                  className="input"
                  rows="3"
                  required
                  placeholder="Ingrese el diagnóstico del paciente"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tratamiento <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={historiaForm.tratamiento}
                  onChange={(e) =>
                    setHistoriaForm((prev) => ({ ...prev, tratamiento: e.target.value }))
                  }
                  className="input"
                  rows="4"
                  required
                  placeholder="Describa el tratamiento prescrito, medicamentos, dosis, etc."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notas Adicionales (opcional)
                </label>
                <textarea
                  value={historiaForm.notas}
                  onChange={(e) =>
                    setHistoriaForm((prev) => ({ ...prev, notas: e.target.value }))
                  }
                  className="input"
                  rows="3"
                  placeholder="Observaciones adicionales, recomendaciones, seguimiento, etc."
                />
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowHistoriaModal(false);
                    setCitaSeleccionada(null);
                    setHistoriaForm({ diagnostico: '', tratamiento: '', notas: '' });
                  }}
                  className="btn btn-secondary flex-1"
                >
                  Cancelar
                </button>
                <button type="submit" className="btn btn-primary flex-1 flex items-center justify-center gap-2">
                  <FileText className="w-4 h-4" />
                  Guardar Entrada
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
