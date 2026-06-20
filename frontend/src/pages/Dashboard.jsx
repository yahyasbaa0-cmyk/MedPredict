import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/useAuthStore';
import api from '../services/api';
import useToastStore from '../store/useToastStore';
import { useThemeStore } from '../store/useThemeStore';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import Spinner from '../components/Spinner';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const StatCard = ({ title, value, subtitle, bgClass, textClass, animationClass = '' }) => (
  <div className={`card card-hover relative overflow-hidden flex flex-col justify-between h-full ${animationClass}`}>
    <div className="absolute top-0 right-0 p-4 opacity-10">
      {/* Decorative element could go here */}
    </div>
    <div>
      <h3 className="text-xs uppercase tracking-wider font-semibold text-muted mb-2">{title}</h3>
      <p className={`text-4xl font-bold tracking-tight mb-0 ${textClass}`}>{value}</p>
    </div>
    {subtitle && <p className="text-sm text-light mt-4 mb-0">{subtitle}</p>}
  </div>
);

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const { addToast } = useToastStore();
  const theme = useThemeStore(state => state.theme);

  // Chart colors based on theme
  const chartColors = {
    light: ['#2563eb', '#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'],
    dark: ['#3b82f6', '#22d3ee', '#34d399', '#fbbf24', '#fb7185', '#a78bfa']
  };
  
  const appointmentColors = {
    light: ['#2563eb', '#10b981', '#ef4444'],
    dark: ['#3b82f6', '#34d399', '#fb7185']
  };

  const getChartColors = () => chartColors[theme] || chartColors.light;
  const getAppointmentColors = () => appointmentColors[theme] || appointmentColors.light;

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get('/dashboard/stats/');
        setStats(res.data);
      } catch (error) {
        console.error("Dashboard error", error);
        addToast('Erreur', 'Impossible de charger le tableau de bord', 'error');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) return <div className="h-full flex items-center justify-center"><Spinner size={40} /></div>;
  if (!stats) return <div className="text-center p-8 text-light font-medium">Erreur de chargement. Veuillez rafraîchir.</div>;

  const { general_activity, pathologies_distribution, appointments_stats, ai_usage } = stats;

  const pathologyData = {
    labels: pathologies_distribution.map(p => p.diagnosis),
    datasets: [
      {
        data: pathologies_distribution.map(p => p.count),
        backgroundColor: getChartColors(),
        borderWidth: 0,
        hoverOffset: 8
      },
    ],
  };

  const appointmentsData = {
    labels: ['Planifiés/En cours', 'Terminés', 'Annulés'],
    datasets: [
      {
        label: 'Rendez-vous',
        data: [
          appointments_stats.total - appointments_stats.completed - appointments_stats.cancelled,
          appointments_stats.completed,
          appointments_stats.cancelled
        ],
        backgroundColor: getAppointmentColors(),
        borderRadius: 8,
        borderSkipped: false,
      }
    ]
  };

  const chartOptions = {
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom', labels: { usePointStyle: true, padding: 20, font: { family: 'Outfit', size: 12 } } },
    },
    cutout: '75%',
  };

  const barOptions = {
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      y: { border: { display: false }, grid: { color: 'rgba(0,0,0,0.05)' }, beginAtZero: true },
      x: { border: { display: false }, grid: { display: false } }
    }
  };

  return (
    <div className="animate-fade-in w-full max-w-full">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-main tracking-tight m-0">Vue d'ensemble</h1>
        <p className="text-muted mt-2">Votre activité en un coup d'œil.</p>
      </div>
      
      <div className="grid grid-cols-4 gap-6 mb-8">
        <StatCard title="Patients Inscrits" value={general_activity.total_patients} textClass="text-primary" animationClass="stagger-1" />
        <StatCard title="RDV Total" value={appointments_stats.total} textClass="text-warning" animationClass="stagger-2" />
        <StatCard title="Consultations (30 jours)" value={general_activity.consultations_last_30d} textClass="text-success" animationClass="stagger-3" />
        <StatCard title="Taux Utilisation IA" value={`${ai_usage.usage_rate}%`} subtitle={`${ai_usage.used_count} diagnostics assistés`} textClass="text-[var(--primary)]" animationClass="stagger-4" />
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="card w-full h-[450px] flex flex-col stagger-5">
          <h2 className="card-title m-0 mb-6">Top 5 Pathologies</h2>
          <div className="flex-1 relative w-full h-full min-h-[300px]">
            {pathologies_distribution.length > 0 ? (
              <Doughnut data={pathologyData} options={chartOptions} />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center text-light">Aucune donnée suffisante</div>
            )}
          </div>
        </div>
        
        <div className="card w-full h-[450px] flex flex-col stagger-5" style={{ animationDelay: "0.6s" }}>
          <h2 className="card-title m-0 mb-6">Statuts des Rendez-vous</h2>
          <div className="flex-1 relative w-full h-full min-h-[300px]">
             <Bar data={appointmentsData} options={barOptions} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
