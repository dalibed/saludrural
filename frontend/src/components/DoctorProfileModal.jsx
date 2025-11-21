import React from 'react';
import { X, Mail, Phone, BadgeCheck, Award, FileCheck } from 'lucide-react';

const getValue = (source, keys, fallback = '') => {
  for (const key of keys) {
    if (source[key] !== undefined && source[key] !== null) {
      return source[key];
    }
  }
  return fallback;
};

const DoctorProfileModal = ({ doctor, onClose }) => {
  if (!doctor) return null;

  const nombre = `${getValue(doctor, ['nombre', 'Nombre'], '')} ${getValue(
    doctor,
    ['apellidos', 'Apellidos'],
    ''
  )}`.trim();
  const descripcion =
    getValue(doctor, ['descripcion_perfil', 'DescripcionPerfil'], '') ||
    'Aún no tenemos una descripción publicada para este profesional.';
  const experiencia = getValue(
    doctor,
    ['anios_experiencia', 'años_experiencia', 'AniosExperiencia'],
    null
  );
  const correo = getValue(doctor, ['correo', 'email', 'Correo']);
  const telefono = getValue(doctor, ['telefono', 'Telefono']);
  const licencia = getValue(doctor, ['licencia', 'Licencia'], 'En validación');
  const estadoValidacion =
    getValue(doctor, ['estado_validacion', 'EstadoValidacion'], 'Pendiente') || 'Pendiente';

  return (
    <div className="fixed inset-0 bg-dark-900/60 backdrop-blur-sm z-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-3xl shadow-2xl max-w-3xl w-full overflow-hidden">
        <div className="flex justify-between items-center px-6 py-4 border-b border-gray-100">
          <h3 className="text-xl font-semibold text-dark-700">{nombre}</h3>
          <button className="p-2 text-dark-400 hover:text-dark-600" onClick={onClose}>
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-6 space-y-6">
          <section>
            <p className="text-dark-500 leading-relaxed">{descripcion}</p>
          </section>

          <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-2xl border border-gray-100 bg-primary-50/60">
              <div className="flex items-center text-primary-700 font-semibold mb-2">
                <Award className="w-5 h-5 mr-2" />
                Experiencia
              </div>
              <p className="text-2xl font-bold text-primary-800">
                {experiencia ? `${experiencia} años` : 'En actualización'}
              </p>
            </div>
            <div className="p-4 rounded-2xl border border-gray-100 bg-white">
              <div className="flex items-center text-dark-500 font-semibold mb-2">
                <BadgeCheck className="w-5 h-5 mr-2 text-primary-600" />
                Estado de validación
              </div>
              <p className="text-lg font-bold text-dark-700">{estadoValidacion}</p>
              <p className="text-xs text-dark-400 mt-1">
                Licencia {licencia || 'N/D'}
              </p>
            </div>
          </section>

          <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-center space-x-3">
              <div className="p-3 rounded-2xl bg-primary-50 text-primary-700">
                <Mail className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs uppercase tracking-wide text-dark-300">Correo</p>
                <p className="text-sm font-semibold text-dark-600">{correo || 'No disponible'}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="p-3 rounded-2xl bg-primary-50 text-primary-700">
                <Phone className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs uppercase tracking-wide text-dark-300">Teléfono</p>
                <p className="text-sm font-semibold text-dark-600">
                  {telefono || 'No disponible'}
                </p>
              </div>
            </div>
          </section>

          <section className="border border-dashed border-primary-200 rounded-2xl p-4 flex items-center space-x-4">
            <FileCheck className="w-10 h-10 text-primary-500" />
            <p className="text-sm text-dark-500">
              Los documentos de {nombre || 'este médico'} están siendo verificados por el
              administrador. Solo los médicos con documentación aprobada pueden recibir pacientes.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
};

export default DoctorProfileModal;

