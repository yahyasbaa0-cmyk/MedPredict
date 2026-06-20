import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/useAuthStore';
import { useThemeStore } from '../store/useThemeStore';
import api from '../services/api';
import useToastStore from '../store/useToastStore';
import { Activity, Calendar, Clock, User, LogOut, CheckCircle, AlertCircle, XCircle, Loader2, CalendarPlus } from 'lucide-react';
import Spinner from '../components/Spinner';
import ThemeToggle from '../components/ThemeToggle';

const PatientPortal = () => {
  const { user } = useAuthStore();
  const logout = useAuthStore(state => state.logout);
  const navigate = useNavigate();
  const { addToast } = useToastStore();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        const res = await api.get('/appointments/my/');
        setAppointments(res.data);
      } catch (err) {
        console.error(err);
        addToast('Erreur', 'Impossible de charger vos rendez-vous.', 'error');
      } finally {
        setLoading(false);
      }
    };
    fetchAppointments();
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getStatusConfig = (status) => {
    switch (status) {
      case 'PLANNED':
        return { label: 'Planifié', icon: Clock, color: 'var(--warning)', bg: 'rgba(245,158,11,0.15)', border: 'rgba(245,158,11,0.3)' };
      case 'CONFIRMED':
        return { label: 'Confirmé', icon: CheckCircle, color: 'var(--primary)', bg: 'rgba(37,99,235,0.15)', border: 'rgba(37,99,235,0.3)' };
      case 'IN_PROGRESS':
        return { label: 'En cours', icon: Loader2, color: 'var(--secondary)', bg: 'rgba(6,182,212,0.15)', border: 'rgba(6,182,212,0.3)' };
      case 'COMPLETED':
        return { label: 'Terminé', icon: CheckCircle, color: 'var(--success)', bg: 'rgba(16,185,129,0.15)', border: 'rgba(16,185,129,0.3)' };
      case 'CANCELLED':
        return { label: 'Annulé', icon: XCircle, color: 'var(--danger)', bg: 'rgba(244,63,94,0.15)', border: 'rgba(244,63,94,0.3)' };
      default:
        return { label: status, icon: AlertCircle, color: 'var(--text-muted)', bg: 'var(--bg-hover)', border: 'var(--glass-border)' };
    }
  };

  const formatDate = (dateStr) => {
    const d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString('fr-FR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  };

  const upcomingAppointments = appointments.filter(a => a.status !== 'CANCELLED' && a.status !== 'COMPLETED');
  const pastAppointments = appointments.filter(a => a.status === 'CANCELLED' || a.status === 'COMPLETED');

  return (
    <div className="app-wrapper-ambient" style={{ minHeight: '100vh' }}>
      <div className="mesh-bg"></div>

      {/* Header */}
      <header
        className="floating-topbar flex justify-between items-center"
        style={{ zIndex: 30, position: 'sticky', top: 0, margin: '1rem 1.5rem 0', borderRadius: 'var(--radius-xl)' }}
      >
        <div className="flex items-center" style={{ gap: '0.75rem' }}>
          <div
            className="flex items-center justify-center"
            style={{
              width: '2.5rem', height: '2.5rem', borderRadius: 'var(--radius-md)',
              background: 'linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%)',
              boxShadow: 'var(--shadow-sm)'
            }}
          >
            <Activity size={20} color="white" />
          </div>
          <h1 className="text-xl font-bold text-main m-0" style={{ fontFamily: 'var(--font-heading)', letterSpacing: '-0.02em' }}>
            Mon Espace Patient
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <ThemeToggle />
          <div style={{ width: '1px', height: '2rem', background: 'var(--glass-border)' }}></div>
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg" style={{ background: 'var(--bg-hover)', border: '1px solid var(--glass-border)' }}>
            <User size={16} style={{ color: 'var(--primary)' }} />
            <span className="text-sm font-semibold text-main">{user?.first_name} {user?.last_name}</span>
          </div>
          <button onClick={handleLogout} className="btn btn-outline-danger" style={{ padding: '0.5rem 1rem' }}>
            <LogOut size={18} strokeWidth={2.5} />
            <span>Déconnexion</span>
          </button>
        </div>
      </header>

      {/* Content */}
      <main style={{ maxWidth: '56rem', margin: '0 auto', padding: '2rem 1.5rem 3rem' }}>

        {/* Welcome card */}
        <div className="card animate-fade-in" style={{
          background: 'linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%)',
          color: 'white',
          border: 'none',
          marginBottom: '2rem'
        }}>
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold m-0 mb-1" style={{ color: 'white' }}>
                Bonjour, {user?.first_name} 👋
              </h2>
              <p className="m-0" style={{ color: 'rgba(255,255,255,0.8)', fontSize: '0.95rem' }}>
                {upcomingAppointments.length > 0
                  ? `Vous avez ${upcomingAppointments.length} rendez-vous à venir.`
                  : 'Vous n\'avez aucun rendez-vous à venir.'
                }
              </p>
            </div>
            <button
              onClick={() => navigate('/book')}
              className="flex items-center gap-2 font-bold"
              style={{
                background: 'rgba(255,255,255,0.2)',
                color: 'white',
                border: '1px solid rgba(255,255,255,0.3)',
                padding: '0.6rem 1.2rem',
                borderRadius: 'var(--radius-lg)',
                cursor: 'pointer',
                transition: 'all 0.2s',
                backdropFilter: 'blur(8px)'
              }}
            >
              <CalendarPlus size={18} /> Nouveau rendez-vous
            </button>
          </div>
        </div>

        {loading ? (
          <div className="card flex items-center justify-center" style={{ minHeight: '200px' }}>
            <Spinner size={40} />
          </div>
        ) : appointments.length === 0 ? (
          <div className="card animate-fade-in text-center" style={{ padding: '4rem 2rem' }}>
            <Calendar size={64} className="mx-auto mb-4" style={{ color: 'var(--primary)', opacity: 0.3 }} />
            <h3 className="text-xl font-bold text-main mb-2">Aucun rendez-vous</h3>
            <p className="text-muted mb-6">Vous n'avez pas encore de rendez-vous enregistré.</p>
            <button onClick={() => navigate('/book')} className="btn btn-primary px-8">
              <CalendarPlus size={18} /> Prendre un rendez-vous
            </button>
          </div>
        ) : (
          <>
            {/* Upcoming */}
            {upcomingAppointments.length > 0 && (
              <div className="animate-fade-in">
                <h3 className="text-lg font-bold text-main mb-4 flex items-center gap-2">
                  <Calendar size={20} style={{ color: 'var(--primary)' }} />
                  Rendez-vous à venir
                </h3>
                <div className="flex flex-col gap-4 mb-8">
                  {upcomingAppointments.map(a => {
                    const sc = getStatusConfig(a.status);
                    const StatusIcon = sc.icon;
                    return (
                      <div key={a.id} className="card card-hover" style={{ borderLeft: `4px solid ${sc.color}`, padding: '1.25rem 1.5rem' }}>
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-3">
                              <div style={{
                                display: 'inline-flex', alignItems: 'center', gap: '0.4rem',
                                background: sc.bg, color: sc.color, border: `1px solid ${sc.border}`,
                                padding: '0.3rem 0.75rem', borderRadius: 'var(--radius-md)',
                                fontSize: '0.8rem', fontWeight: 700
                              }}>
                                <StatusIcon size={14} />
                                {sc.label}
                              </div>
                            </div>
                            <div className="flex items-center gap-2 mb-2">
                              <Calendar size={16} style={{ color: 'var(--primary)' }} />
                              <span className="font-semibold text-main" style={{ textTransform: 'capitalize' }}>
                                {formatDate(a.date)}
                              </span>
                            </div>
                            <div className="flex items-center gap-2 mb-2">
                              <Clock size={16} style={{ color: 'var(--text-muted)' }} />
                              <span className="text-muted">
                                {a.time.substring(0, 5)} — {a.duration} minutes
                              </span>
                            </div>
                            <div className="flex items-center gap-2">
                              <User size={16} style={{ color: 'var(--text-muted)' }} />
                              <span className="text-muted">
                                {a.doctor_details ? `Dr. ${a.doctor_details.first_name} ${a.doctor_details.last_name}` : `Docteur #${a.doctor}`}
                              </span>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-muted m-0 font-medium" style={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                              Motif
                            </p>
                            <p className="text-sm text-main m-0 mt-1 font-medium">{a.reason}</p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Past */}
            {pastAppointments.length > 0 && (
              <div className="animate-fade-in">
                <h3 className="text-lg font-bold text-muted mb-4 flex items-center gap-2">
                  <Clock size={20} style={{ color: 'var(--text-light)' }} />
                  Historique
                </h3>
                <div className="flex flex-col gap-3">
                  {pastAppointments.map(a => {
                    const sc = getStatusConfig(a.status);
                    const StatusIcon = sc.icon;
                    return (
                      <div key={a.id} className="card" style={{
                        padding: '1rem 1.25rem',
                        opacity: 0.7,
                        borderLeft: `3px solid ${sc.color}`
                      }}>
                        <div className="flex justify-between items-center">
                          <div className="flex items-center gap-4">
                            <div style={{
                              display: 'inline-flex', alignItems: 'center', gap: '0.3rem',
                              background: sc.bg, color: sc.color, border: `1px solid ${sc.border}`,
                              padding: '0.2rem 0.6rem', borderRadius: 'var(--radius-md)',
                              fontSize: '0.75rem', fontWeight: 700
                            }}>
                              <StatusIcon size={12} />
                              {sc.label}
                            </div>
                            <span className="text-sm font-medium text-main" style={{ textTransform: 'capitalize' }}>
                              {formatDate(a.date)}
                            </span>
                            <span className="text-sm text-muted">{a.time.substring(0, 5)}</span>
                          </div>
                          <span className="text-sm text-muted">
                            {a.doctor_details ? `Dr. ${a.doctor_details.last_name}` : ''}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
};

export default PatientPortal;
