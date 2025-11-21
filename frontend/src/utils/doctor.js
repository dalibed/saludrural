const getValue = (source, keys, fallback = '') => {
  for (const key of keys) {
    if (source[key] !== undefined && source[key] !== null && source[key] !== '') {
      return source[key];
    }
  }
  return fallback;
};

export const normalizeDoctor = (doctor = {}) => {
  if (doctor?.raw) {
    return doctor;
  }
  const nombre = getValue(doctor, ['nombre', 'Nombre'], '');
  const apellidos = getValue(doctor, ['apellidos', 'Apellidos'], '');
  const fullName = `${nombre} ${apellidos}`.trim() || getValue(doctor, ['nombre_completo', 'NombreCompleto'], '');
  const especialidad =
    getValue(doctor, ['especialidad', 'Especialidad', 'especialidad_principal', 'EspecialidadPrincipal'], '') ||
    'Medicina General';
  const vereda = getValue(doctor, ['vereda', 'Vereda', 'municipio', 'Municipio'], 'Colombia');
  const ratingRaw = getValue(
    doctor,
    ['promedio_calificacion', 'PromedioCalificacion', 'promedio', 'Promedio', 'promedio_calificaciones'],
    null
  );
  const rating = ratingRaw ? Number(ratingRaw) : null;
  const totalCitas = Number(
    getValue(doctor, ['total_citas', 'TotalCitas', 'citas_atendidas', 'CitasAtendidas'], null)
  );
  const estadoValidacion = getValue(doctor, ['estado_validacion', 'EstadoValidacion'], '');
  const idMedico = doctor.id_medico || doctor.ID_Medico || doctor.id || doctor.ID;
  const usuarioId =
    doctor.id_usuario?.id_usuario ||
    doctor.id_usuario ||
    doctor.ID_Usuario ||
    doctor.id_usuario_medico ||
    doctor.ID_Usuario_Medico ||
    null;

  return {
    raw: doctor,
    id: idMedico || usuarioId,
    usuarioId,
    nombre: fullName || `Médico ${idMedico || ''}`.trim(),
    especialidad,
    vereda,
    rating,
    totalCitas: Number.isNaN(totalCitas) ? null : totalCitas,
    estadoValidacion,
    iniciales: fullName
      ? fullName
          .split(' ')
          .filter(Boolean)
          .slice(0, 2)
          .map((part) => part[0]?.toUpperCase() || '')
          .join('')
      : 'SR',
  };
};

