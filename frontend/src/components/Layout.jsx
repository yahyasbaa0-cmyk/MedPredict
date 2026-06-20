import React from 'react';
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import useAuthStore from '../store/useAuthStore';
import { Home, Users, Calendar, FileText, LogOut, Activity, User, Bell, CheckCircle2 } from 'lucide-react';
import api from '../services/api';
import ChatbotButton from './ChatbotButton';
import ChatbotWindow from './ChatbotWindow';
import ThemeToggle from './ThemeToggle';

const Sidebar = () => {
  const { user } = useAuthStore();
  
  const navItems = [
    { to: '/', label: 'Dashboard', icon: Home, roles: ['ADMIN', 'DOCTOR', 'SECRETARY'] },
    { to: '/patients', label: 'Patients', icon: Users, roles: ['ADMIN', 'DOCTOR', 'SECRETARY'] },
    { to: '/appointments', label: 'Agenda', icon: Calendar, roles: ['ADMIN', 'DOCTOR', 'SECRETARY'] },
    { to: '/consultations', label: 'Consultations', icon: Activity, roles: ['DOCTOR', 'ADMIN'] },
    { to: '/prescriptions', label: 'Ordonnances', icon: FileText, roles: ['DOCTOR', 'SECRETARY', 'ADMIN'] },
  ];

  return (
    <aside className="floating-sidebar" style={{ zIndex: 20 }}>
      {/* Brand */}
      <div className="flex items-center p-6 m-0" style={{ gap: '1rem', borderBottom: '1px solid var(--glass-border)' }}>
        <div className="flex items-center justify-center p-2 rounded-lg" style={{ background: 'var(--primary-light)', border: '1px solid rgba(255,255,255,0.4)', boxShadow: 'var(--shadow-sm)' }}>
           <Activity className="text-primary" size={26} strokeWidth={2.5} />
        </div>
        <h2 className="text-2xl text-main m-0" style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, letterSpacing: '-0.02em' }}>MedPredict</h2>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 overflow-y-auto">
        <ul className="m-0 p-0 flex flex-col gap-2" style={{ listStyle: 'none' }}>
          {navItems.filter(item => item.roles.includes(user?.role)).map((item) => (
            <li key={item.to}>
              <NavLink 
                to={item.to}
                className={({isActive}) => `flex items-center px-4 py-3 rounded-lg font-semibold hover-scale ${isActive ? 'text-primary' : 'text-muted'}`}
                style={({isActive}) => ({
                  gap: '0.85rem',
                  background: isActive ? 'white' : 'transparent',
                  boxShadow: isActive ? 'var(--shadow-sm)' : 'none',
                  border: isActive ? '1px solid rgba(0,0,0,0.05)' : '1px solid transparent'
                })}
              >
                <item.icon size={20} strokeWidth={2.5} />
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      
      {/* User Profile */}
      <div className="p-6" style={{ borderTop: '1px solid var(--glass-border)', background: 'rgba(255,255,255,0.4)' }}>
        <div className="flex items-center p-3 rounded-lg hover-scale cursor-pointer" style={{ gap: '0.75rem', background: 'rgba(255,255,255,0.6)', border: '1px solid white', boxShadow: 'var(--shadow-sm)' }}>
          <div className="p-2 rounded-md" style={{ background: 'linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%)', boxShadow: 'var(--shadow-sm)' }}>
            <User color="white" size={18} strokeWidth={2.5} />
          </div>
          <div className="flex-1 overflow-hidden">
            <p className="text-sm font-bold text-main m-0 truncate" style={{ fontFamily: 'var(--font-base)' }}>{user?.first_name} {user?.last_name}</p>
            <p className="text-xs text-primary m-0 mt-1" style={{ textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 800 }}>{user?.role}</p>
          </div>
        </div>
      </div>
    </aside>
  );
};

const Topbar = () => {
  const logout = useAuthStore(state => state.logout);
  const navigate = useNavigate();
  const location = useLocation();
  const [notifications, setNotifications] = React.useState([]);
  const [showNotifications, setShowNotifications] = React.useState(false);

  const fetchNotifications = async () => {
    try {
      const res = await api.get('/auth/notifications/');
      setNotifications(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  React.useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleMarkAllRead = async () => {
    try {
      await api.patch('/auth/notifications/mark_all_read/');
      fetchNotifications();
    } catch (err) {
      console.error(err);
    }
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getPageTitle = () => {
    const path = location.pathname;
    if(path === '/') return 'Vue d\'ensemble';
    if(path.startsWith('/patients')) return 'Dossiers Patients';
    if(path.startsWith('/appointments')) return 'Agenda & Rendez-vous';
    if(path.startsWith('/consultations')) return 'Intelligence Artificielle';
    if(path.startsWith('/prescriptions')) return 'Ordonnances Médicales';
    return 'Système';
  };

  return (
    <header className="floating-topbar flex justify-between items-center" style={{ zIndex: 30 }}>
      <div className="flex items-center">
        <h1 className="text-xl font-bold text-main m-0" style={{ fontFamily: 'var(--font-heading)', letterSpacing: '-0.02em', background: 'transparent', boxShadow: 'none' }}>
          {getPageTitle()}
        </h1>
      </div>

      <div className="flex items-center gap-4">
        {/* Notification Bell */}
        <div className="relative">
          <button 
            onClick={() => setShowNotifications(!showNotifications)}
            className="btn-icon hover-scale relative" 
            style={{ background: 'rgba(255,255,255,0.5)', border: '1px solid rgba(255,255,255,0.8)', boxShadow: 'var(--shadow-sm)', color: 'var(--text-muted)' }}
          >
            {unreadCount > 0 && (
              <span className="absolute animate-pulse" style={{ width: '8px', height: '8px', background: 'var(--danger)', borderRadius: '50%', top: '6px', right: '6px' }}></span>
            )}
            <Bell size={20} strokeWidth={2.5} />
          </button>
          
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden" style={{ zIndex: 100, backdropFilter: 'blur(20px)', background: 'rgba(255,255,255,0.95)' }}>
              <div className="flex justify-between items-center p-4 border-b border-gray-100 bg-gray-50/50">
                <h3 className="font-bold text-gray-800 m-0">Notifications</h3>
                {unreadCount > 0 && (
                  <button onClick={handleMarkAllRead} className="text-xs text-primary font-medium flex items-center gap-1 hover:text-blue-700">
                    <CheckCircle2 size={14} /> Tout marquer lu
                  </button>
                )}
              </div>
              <div className="max-h-80 overflow-y-auto">
                {notifications.length === 0 ? (
                  <p className="text-sm text-gray-500 p-4 text-center m-0">Aucune notification.</p>
                ) : (
                  notifications.map(n => (
                    <div key={n.id} className={`p-4 border-b border-gray-50 ${!n.is_read ? 'bg-blue-50/30' : ''}`}>
                      <p className={`text-sm m-0 ${!n.is_read ? 'font-bold text-gray-800' : 'text-gray-600'}`}>{n.message}</p>
                      <p className="text-xs text-gray-400 mt-1 m-0">{new Date(n.created_at).toLocaleString()}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        
        {/* Divider */}
        <div style={{ width: '1px', height: '2rem', background: 'var(--glass-border)', margin: '0 0.25rem' }}></div>
        
        {/* Theme Toggle */}
        <ThemeToggle />
        
        {/* Divider */}
        <div style={{ width: '1px', height: '2rem', background: 'var(--glass-border)', margin: '0 0.25rem' }}></div>
        
        {/* Logout */}
        <button onClick={handleLogout} className="btn btn-outline-danger" style={{ padding: '0.5rem 1rem' }}>
          <LogOut size={18} strokeWidth={2.5} />
          <span>Déconnexion</span>
        </button>
      </div>
    </header>
  );
};

const Layout = () => {
  return (
    <div className="app-wrapper-ambient">
      <div className="mesh-bg"></div>
      <div className="app-container">
        <Sidebar />
        <div className="app-main">
          <Topbar />
          <main className="app-content stagger-2">
            <div style={{ maxWidth: '80rem', margin: '0 auto', paddingBottom: '2.5rem' }}>
              <Outlet />
            </div>
          </main>
        </div>
      </div>
      {/* Chatbot Components */}
      <ChatbotButton />
      <ChatbotWindow />
    </div>
  );
};

export default Layout;
