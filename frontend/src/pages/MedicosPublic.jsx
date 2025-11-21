import React, { useEffect, useMemo, useState } from 'react';
import { Search, Filter } from 'lucide-react';
import DoctorCard from '../components/DoctorCard';
import DoctorProfileModal from '../components/DoctorProfileModal';
import BookAppointmentModal from '../components/BookAppointmentModal';
import { medicoService, especialidadService } from '../services/api';
import { normalizeDoctor } from '../utils/doctor';

const MedicosPublic = () => {
  const [medicos, setMedicos] = useState([]);
  const [search, setSearch] = useState('');
  const [especialidades, setEspecialidades] = useState([]);
  const [selectedEspecialidad, setSelectedEspecialidad] = useState('todos');
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [bookingDoctor, setBookingDoctor] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [medicosData, especialidadesData] = await Promise.all([
          medicoService.getByEstado('Aprobado').catch(() => []),
          especialidadService.list().catch(() => []),
        ]);
        const normalized = Array.isArray(medicosData) ? medicosData.map(normalizeDoctor) : [];
        setMedicos(normalized);
        setEspecialidades(Array.isArray(especialidadesData) ? especialidadesData : []);
      } catch (error) {
        console.error('Error al cargar médicos públicos', error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const filteredMedicos = useMemo(() => {
    return medicos.filter((medico) => {
      const fullName = (medico.nombre || '').toLowerCase();
      const specialty = medico.especialidad?.toLowerCase() || '';
      const matchesSearch = fullName.includes(search.toLowerCase());
      const matchesSpecialty =
        selectedEspecialidad === 'todos' ||
        specialty.includes(selectedEspecialidad.toLowerCase());
      return matchesSearch && matchesSpecialty;
    });
  }, [medicos, search, selectedEspecialidad]);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="mb-10">
        <p className="chip mb-3">Directorio de especialistas</p>
        <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-6">
          <div>
            <h1 className="text-4xl font-bold text-dark-800 mb-2">Encuentra tu médico ideal</h1>
            <p className="text-dark-500 max-w-2xl">
              Lista pública en tonos blancos y verdes para que puedas explorar antes de iniciar sesión.
              Cada tarjeta muestra nombre, especialidad, calificación promedio y accesos rápidos.
            </p>
          </div>
          <div className="flex space-x-4">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-dark-300 absolute left-4 top-1/2 -translate-y-1/2" />
              <input
                className="input pl-10"
                placeholder="Buscar por nombre"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="relative min-w-[200px]">
              <Filter className="w-4 h-4 text-dark-300 absolute left-4 top-1/2 -translate-y-1/2" />
              <select
                className="input pl-10 appearance-none"
                value={selectedEspecialidad}
                onChange={(e) => setSelectedEspecialidad(e.target.value)}
              >
                <option value="todos">Todas las especialidades</option>
                {especialidades.map((esp) => (
                  <option key={esp.id_especialidad || esp.ID_Especialidad} value={esp.nombre || esp.Nombre}>
                    {esp.nombre || esp.Nombre}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-200 border-t-primary-500" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredMedicos.map((medico) => (
            <DoctorCard
              key={medico.id || medico.usuarioId}
              doctor={medico}
              onViewProfile={setSelectedDoctor}
              onBook={setBookingDoctor}
            />
          ))}
        </div>
      )}

      {filteredMedicos.length === 0 && !loading && (
        <p className="text-center text-dark-400 py-10">
          No encontramos médicos con ese criterio de búsqueda.
        </p>
      )}

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
    </div>
  );
};

export default MedicosPublic;

