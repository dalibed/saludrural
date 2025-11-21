import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { HeartPulse, Book, UsersRound, Shield, Stethoscope, FileText, Calendar } from 'lucide-react';
import DoctorCard from '../components/DoctorCard';
import DoctorProfileModal from '../components/DoctorProfileModal';
import BookAppointmentModal from '../components/BookAppointmentModal';
import { medicoService, diccionarioService } from '../services/api';
import { normalizeDoctor } from '../utils/doctor';

const sections = [
  {
    title: 'Pacientes',
    description: 'Encuentra médicos certificados disponibles para videoconsultas y seguimiento.',
    icon: HeartPulse,
    color: 'bg-primary-50 text-primary-700',
  },
  {
    title: 'Médicos',
    description: 'Gestiona tu agenda, valida documentos y atiende a todo el país.',
    icon: Stethoscope,
    color: 'bg-accent-50 text-accent-700',
  },
  {
    title: 'Administrador',
    description: 'Supervisa validaciones, documentos y notificaciones del ecosistema.',
    icon: Shield,
    color: 'bg-dark-50 text-dark-600',
  },
];

const Home = () => {
  const [medicos, setMedicos] = useState([]);
  const [diccionarioPreview, setDiccionarioPreview] = useState([]);
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [bookingDoctor, setBookingDoctor] = useState(null);
  const [loadingDoctors, setLoadingDoctors] = useState(true);

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoadingDoctors(true);
        const [medicosData, diccionarioData] = await Promise.all([
          medicoService.getByEstado('Aprobado').catch(() => []),
          diccionarioService.list().catch(() => []),
        ]);
        const normalized = Array.isArray(medicosData) ? medicosData.map(normalizeDoctor) : [];
        setMedicos(normalized.slice(0, 6));
        setDiccionarioPreview(Array.isArray(diccionarioData) ? diccionarioData.slice(0, 3) : []);
      } catch (error) {
        console.error('Error cargando landing:', error);
      } finally {
        setLoadingDoctors(false);
      }
    };
    loadInitialData();
  }, []);

  return (
    <div className="bg-white">
      <section className="bg-gradient-to-br from-primary-50 via-white to-accent-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div>
            <div className="inline-flex items-center px-3 py-1 rounded-full bg-white shadow text-primary-600 text-sm font-semibold mb-4">
              Inspirado en la experiencia Top Doctors
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-dark-800 leading-tight mb-6">
              Salud Rural: atención médica confiable con enfoque humano
            </h1>
            <p className="text-lg text-dark-500 mb-8">
              Conectamos pacientes y médicos certificados de todo el país, con una experiencia
              digital en tonos blanco y verde, pensada para inspirar confianza y bienestar.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/medicos" className="btn btn-primary text-base h-12">
                Ver médicos disponibles
              </Link>
              <Link to="/diccionario" className="btn btn-secondary text-base h-12">
                Diccionario médico
              </Link>
            </div>
          </div>
          <div className="bg-white rounded-3xl shadow-2xl border border-primary-100 p-8 space-y-6">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 rounded-2xl bg-primary-600 text-white flex items-center justify-center text-2xl font-bold">
                SR
              </div>
              <div>
                <p className="text-sm text-dark-400">Pacientes activos</p>
                <p className="text-3xl font-semibold text-dark-700">+1.200</p>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              {[
                { label: 'Médicos validados', value: '85', icon: UsersRound },
                { label: 'Especialidades', value: '25', icon: Book },
                { label: 'Municipios', value: '44', icon: Shield },
              ].map((item) => (
                <div key={item.label} className="p-4 rounded-2xl border border-gray-100">
                  <item.icon className="w-5 h-5 text-primary-600 mb-2" />
                  <p className="text-2xl font-bold text-dark-700">{item.value}</p>
                  <p className="text-xs text-dark-400">{item.label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-dark-800 mb-2">Una interfaz limpia y confiable</h2>
        <p className="text-dark-500 mb-10">
          Blanca, verde y liviana, para que pacientes, médicos y administradores tengan claridad en
          cada paso.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {sections.map((section) => (
            <div key={section.title} className="card">
              <div className={`w-12 h-12 rounded-2xl ${section.color} flex items-center justify-center mb-4`}>
                <section.icon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-semibold text-dark-700 mb-2">{section.title}</h3>
              <p className="text-sm text-dark-500">{section.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="bg-primary-50 py-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-10">
            <div>
              <p className="chip mb-2">Atención inmediata</p>
              <h2 className="text-3xl font-bold text-dark-800">Médicos disponibles ya mismo</h2>
              <p className="text-dark-500">
                Disponibles sin login para que puedas conocerlos y decidir con tranquilidad.
              </p>
            </div>
            <Link to="/medicos" className="hidden md:inline-flex btn btn-secondary">
              Ver todos
            </Link>
          </div>
          {loadingDoctors ? (
            <div className="flex justify-center py-10">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-200 border-t-primary-500" />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {medicos.map((medico) => (
                <DoctorCard
                  key={medico.id || medico.usuarioId}
                  doctor={medico}
                  onViewProfile={setSelectedDoctor}
                  onBook={setBookingDoctor}
                />
              ))}
            </div>
          )}
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16 grid grid-cols-1 lg:grid-cols-2 gap-10">
        <div className="card">
          <p className="chip mb-3">Diccionario abierto</p>
          <h3 className="text-2xl font-bold text-dark-800 mb-2">Consulta términos médicos</h3>
          <p className="text-dark-500 mb-6">
            El diccionario está disponible sin iniciar sesión para que cualquier paciente resuelva
            dudas antes de agendar.
          </p>
          <div className="space-y-4">
            {diccionarioPreview.map((termino) => (
              <div key={termino.ID_Diccionario || termino.id_diccionario} className="border border-gray-100 rounded-2xl p-4">
                <p className="font-semibold text-dark-700">{termino.Termino || termino.termino}</p>
                <p className="text-sm text-dark-500 mt-1 line-clamp-2">
                  {termino.Definicion || termino.definicion}
                </p>
              </div>
            ))}
          </div>
          <Link to="/diccionario" className="btn btn-primary w-full mt-6">
            Abrir diccionario completo
          </Link>
        </div>
        <div className="card bg-gradient-to-br from-white to-primary-50">
          <p className="chip mb-3">Flujo validado</p>
          <h3 className="text-2xl font-bold text-dark-800 mb-6">
            Así trabajamos pacientes y médicos
          </h3>
          <ul className="space-y-4">
            {[
              'Regístrate, completa tu perfil y sube documentos.',
              'El administrador valida cada archivo. Estado visible en todo momento.',
              'Cuando todo está aprobado, activas tu agenda y marcas tiempos no disponibles.',
              'Pacientes agendan → médico recibe notificación → genera link de videollamada.',
              'Durante la cita, el médico consulta historia clínica y al finalizar crea la entrada.',
              'Paciente recibe notificación para calificar la atención recibida.',
            ].map((step, index) => (
              <li key={index} className="flex items-start space-x-3">
                <span className="w-8 h-8 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center font-semibold">
                  {index + 1}
                </span>
                <p className="text-sm text-dark-600">{step}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="bg-dark-900 text-white py-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              title: 'Citas y agenda inteligente',
              description: 'El paciente ve la agenda del médico, reserva, cancela y consulta videollamada.',
              icon: Calendar,
            },
            {
              title: 'Perfil editable',
              description: 'Toda la información del paciente en un solo lugar, editable y segura.',
              icon: UsersRound,
            },
            {
              title: 'Historia clínica completa',
              description: 'Entradas creadas por cada médico, antecedentes editables solo por el profesional a cargo.',
              icon: FileText,
            },
          ].map((item) => (
            <div key={item.title} className="p-6 rounded-3xl bg-white/5 border border-white/10">
              <item.icon className="w-8 h-8 text-primary-300 mb-4" />
              <h4 className="text-xl font-semibold mb-3">{item.title}</h4>
              <p className="text-sm text-gray-300">{item.description}</p>
            </div>
          ))}
        </div>
      </section>

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

export default Home;

