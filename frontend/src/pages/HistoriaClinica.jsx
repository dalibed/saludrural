import React, { useEffect, useState } from 'react';
import { ClipboardList, Activity, FileText, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { historiaClinicaService, historiaEntradaService } from '../services/api';

const HistoriaClinica = () => {
  const { user } = useAuth();
  const [historia, setHistoria] = useState(null);
  const [entradas, setEntradas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadHistoria = async () => {
      if (!user) return;

      try {
        setLoading(true);
        const [historiaData, entradasData] = await Promise.all([
          historiaClinicaService.getHistoriaPaciente(user.id_usuario),
          historiaEntradaService.listByPaciente(user.id_usuario),
        ]);
        setHistoria(historiaData || {});
        setEntradas(Array.isArray(entradasData) ? entradasData : []);
      } catch (err) {
        console.error('Error cargando historia clínica', err);
        setError(
          err.response?.data?.detail ||
            'No pudimos obtener tu historia clínica. Intenta nuevamente más tarde.'
        );
      } finally {
        setLoading(false);
      }
    };

    loadHistoria();
  }, [user]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-80">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-200 border-t-primary-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="card flex items-center space-x-3 text-red-600">
        <AlertCircle className="w-6 h-6" />
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-dark-800">Historia clínica</h1>
          <p className="text-dark-500">Tu información médica centralizada, solo lectura.</p>
        </div>
      </div>

      <section className="card">
        <div className="flex items-center mb-4">
          <ClipboardList className="w-6 h-6 text-primary-600 mr-3" />
          <h2 className="text-xl font-semibold text-dark-700">Resumen clínico</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-2xl border border-gray-100 bg-primary-50/70">
            <p className="text-xs uppercase text-dark-400">Antecedentes</p>
            <p className="text-sm text-dark-700 mt-2 whitespace-pre-wrap">
              {historia?.Antecedentes || historia?.antecedentes || 'Sin antecedentes registrados.'}
            </p>
          </div>
          <div className="p-4 rounded-2xl border border-gray-100">
            <p className="text-xs uppercase text-dark-400">Alergias</p>
            <p className="text-sm text-dark-700 mt-2 whitespace-pre-wrap">
              {historia?.Alergias || historia?.alergias || 'Sin alergias reportadas.'}
            </p>
          </div>
        </div>
      </section>

      <section>
        <div className="flex items-center mb-4">
          <FileText className="w-6 h-6 text-primary-600 mr-3" />
          <h2 className="text-xl font-semibold text-dark-700">Entradas médicas</h2>
        </div>
        {entradas.length === 0 ? (
          <div className="card text-center text-dark-400 py-10">
            Aún no existen entradas en tu historia clínica.
          </div>
        ) : (
          <div className="space-y-4">
            {entradas.map((entrada) => (
              <article
                key={entrada.ID_Entrada || entrada.id_entrada}
                className="card border border-gray-100"
              >
                <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Activity className="w-5 h-5 text-primary-600" />
                    <div>
                      <p className="text-sm text-dark-400">
                        {entrada.Fecha || entrada.fecha || 'Fecha no disponible'}
                      </p>
                      <p className="text-base font-semibold text-dark-700">
                        {entrada.MedicoNombre || entrada.medico_nombre || 'Médico'}
                      </p>
                    </div>
                  </div>
                  <span className="chip mt-3 md:mt-0">
                    Cita #{entrada.ID_Cita || entrada.id_cita}
                  </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-dark-600">
                  <div>
                    <p className="font-semibold text-dark-500">Diagnóstico</p>
                    <p className="mt-1 whitespace-pre-wrap">
                      {entrada.Diagnostico || entrada.diagnostico}
                    </p>
                  </div>
                  <div>
                    <p className="font-semibold text-dark-500">Tratamiento</p>
                    <p className="mt-1 whitespace-pre-wrap">
                      {entrada.Tratamiento || entrada.tratamiento}
                    </p>
                  </div>
                </div>
                {entrada.Notas && (
                  <p className="text-xs text-dark-400 mt-3">
                    Notas: {entrada.Notas}
                  </p>
                )}
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

export default HistoriaClinica;

