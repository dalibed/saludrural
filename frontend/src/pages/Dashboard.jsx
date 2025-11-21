import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { citaService, pacienteService, medicoService } from '../services/api';
import {
  Calendar,
  Users,
  Stethoscope,
  Clock,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    citasHoy: 0,
    citasPendientes: 0,
    pacientes: 0,
    medicos: 0,
  });
  const [proximasCitas, setProximasCitas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [citas, pacientes, medicos] = await Promise.all([
        citaService.getAll(),
        pacienteService.getAll(),
        medicoService.getAll(),
      ]);

      const hoy = new Date().toISOString().split('T')[0];
      const citasHoy = citas.filter((cita) => cita.fecha === hoy);
      const citasPendientes = citas.filter(
        (cita) => cita.estado === 'Programada'
      );

      // Obtener próximas citas (próximas 5)
      const proximas = citas
        .filter((cita) => new Date(cita.fecha) >= new Date())
        .sort((a, b) => new Date(a.fecha) - new Date(b.fecha))
        .slice(0, 5);

      setStats({
        citasHoy: citasHoy.length,
        citasPendientes: citasPendientes.length,
        pacientes: pacientes.length,
        medicos: medicos.length,
      });

      setProximasCitas(proximas);
    } catch (error) {
      console.error('Error al cargar datos del dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Citas Hoy',
      value: stats.citasHoy,
      icon: Calendar,
      color: 'bg-blue-500',
    },
    {
      title: 'Citas Pendientes',
      value: stats.citasPendientes,
      icon: Clock,
      color: 'bg-yellow-500',
    },
    {
      title: 'Pacientes',
      value: stats.pacientes,
      icon: Users,
      color: 'bg-green-500',
    },
    {
      title: 'Médicos',
      value: stats.medicos,
      icon: Stethoscope,
      color: 'bg-purple-500',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">
          Bienvenido, {user?.nombre} {user?.apellidos}
        </p>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <div key={index} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">
                  {stat.title}
                </p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {stat.value}
                </p>
              </div>
              <div className={`${stat.color} p-3 rounded-lg`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Próximas Citas */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Próximas Citas
        </h2>
        {proximasCitas.length > 0 ? (
          <div className="space-y-3">
            {proximasCitas.map((cita) => (
              <div
                key={cita.id_cita}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex-1">
                  <p className="font-medium text-gray-900">
                    {cita.paciente_nombre || 'Paciente'}
                  </p>
                  <p className="text-sm text-gray-600">
                    {cita.medico_nombre || 'Médico'}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-medium text-gray-900">
                    {format(new Date(cita.fecha), 'dd MMM yyyy', {
                      locale: es,
                    })}
                  </p>
                  <p className="text-sm text-gray-600">{cita.hora}</p>
                </div>
                <div className="ml-4">
                  {cita.estado === 'Programada' ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-500" />
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">
            No hay citas programadas
          </p>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
