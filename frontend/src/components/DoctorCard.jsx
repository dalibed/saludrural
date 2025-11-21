import React from 'react';
import { Star, Stethoscope, MapPin } from 'lucide-react';
import { normalizeDoctor } from '../utils/doctor';

const DoctorCard = ({ doctor, onViewProfile, onBook }) => {
  const normalized = normalizeDoctor(doctor);
  const nombre = normalized.nombre;
  const especialidad = normalized.especialidad;
  const vereda = normalized.vereda;
  const rating = normalized.rating || 0;
  const totalCitas = normalized.totalCitas;

  return (
    <div className="card h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <span className="chip">{especialidad}</span>
        {rating > 0 ? (
          <span className="inline-flex items-center text-sm font-semibold text-amber-500">
            <Star className="w-4 h-4 mr-1 fill-amber-400 text-amber-400" />
            {rating.toFixed(1)}
          </span>
        ) : (
          <span className="text-xs text-dark-300">Sin calificaciones</span>
        )}
      </div>
      <div className="flex items-center space-x-4 mb-5">
        <div className="w-14 h-14 rounded-2xl bg-primary-100 flex items-center justify-center text-primary-700 font-bold text-lg">
          {normalized.iniciales}
        </div>
        <div>
          <p className="text-lg font-bold text-dark-700">{nombre}</p>
          <p className="text-sm text-dark-400 flex items-center">
            <MapPin className="w-4 h-4 mr-1" />
            {vereda}
          </p>
        </div>
      </div>
      <p className="text-sm text-dark-500 flex items-center mb-4">
        <Stethoscope className="w-4 h-4 mr-2 text-primary-600" />
        Atención en línea y presencial
      </p>

      {totalCitas !== null && (
        <p className="text-xs text-dark-400 mb-4">
          {totalCitas} pacientes atendidos en Salud Rural
        </p>
      )}

      <div className="mt-auto flex flex-col space-y-3">
        <button className="btn btn-secondary" onClick={() => onViewProfile(normalized.raw || doctor)}>
          Ver perfil
        </button>
        <button className="btn btn-primary" onClick={() => onBook(normalized.raw || doctor)}>
          Agendar cita
        </button>
      </div>
    </div>
  );
};

export default DoctorCard;

