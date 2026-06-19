import React, { useState } from 'react';
import useAuthStore from '../store/useAuthStore';
import useToastStore from '../store/useToastStore';
import { useNavigate } from 'react-router-dom';
import { Activity, ShieldCheck, Mail, Lock } from 'lucide-react';
import Spinner from '../components/Spinner';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const login = useAuthStore((state) => state.login);
  const { addToast } = useToastStore();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const success = await login(username, password);
    setLoading(false);
    
    if (success) {
      addToast('Connexion réussie', 'Bienvenue sur MedPredict', 'success');
      navigate('/');
    } else {
      addToast('Accès refusé', 'Identifiants invalides ou serveur injoignable.', 'error');
    }
  };

  return (
    <div 
      className="relative flex items-center justify-center overflow-hidden w-full"
      style={{ backgroundColor: '#0f172a', minHeight: '100vh' }}
    >
      
      {/* Animated Background Blobs */}
      <div className="bg-blob bg-blob-1"></div>
      <div className="bg-blob bg-blob-2"></div>
      <div className="bg-blob bg-blob-3"></div>

      {/* Main Glass Panel */}
      <div 
        className="glass-panel relative z-10 animate-slide-up flex flex-col items-center"
        style={{ width: '100%', maxWidth: '450px', padding: '3rem 2rem', margin: '1rem', borderRadius: '1.5rem' }}
      >
        
        <div 
          className="flex items-center justify-center hover-scale mb-6"
          style={{ width: '4rem', height: '4rem', borderRadius: '1rem', background: 'linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%)', boxShadow: '0 10px 25px -5px rgba(37,99,235,0.4)' }}
        >
          <Activity size={32} color="white" />
        </div>
        
        <h2 className="text-3xl text-main text-center m-0 mb-1" style={{ fontWeight: 900, letterSpacing: '-0.05em' }}>MedPredict</h2>
        <p className="text-muted text-center text-sm font-medium mb-8">Plateforme d'Intelligence Médicale</p>
        
        <form onSubmit={handleSubmit} className="w-full flex flex-col gap-4">
          <div>
            <div className="relative">
              <div className="absolute flex items-center" style={{ left: '1rem', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }}>
                <Mail size={18} className="text-muted" />
              </div>
              <input 
                type="text" 
                className="input" 
                style={{ paddingLeft: '3rem', paddingTop: '0.8rem', paddingBottom: '0.8rem', backgroundColor: 'rgba(255,255,255,0.6)', borderColor: 'rgba(255,255,255,0.5)', fontWeight: 500 }}
                placeholder="Identifiant de connexion"
                value={username} 
                onChange={e => setUsername(e.target.value)} 
                required 
              />
            </div>
          </div>
          
          <div>
            <div className="relative">
              <div className="absolute flex items-center" style={{ left: '1rem', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }}>
                <Lock size={18} className="text-muted" />
              </div>
              <input 
                type="password" 
                className="input" 
                style={{ paddingLeft: '3rem', paddingTop: '0.8rem', paddingBottom: '0.8rem', backgroundColor: 'rgba(255,255,255,0.6)', borderColor: 'rgba(255,255,255,0.5)', fontWeight: 500 }}
                placeholder="Mot de passe"
                value={password} 
                onChange={e => setPassword(e.target.value)} 
                required 
              />
            </div>
          </div>
          
          <button 
            type="submit" 
            className="btn btn-primary w-full mt-4 text-base pulse-primary relative overflow-hidden" 
            style={{ paddingTop: '0.8rem', paddingBottom: '0.8rem', boxShadow: '0 8px 20px -4px rgba(37,99,235,0.4)', border: 'none' }}
            disabled={loading}
          >
            {loading ? <Spinner size={20} className="text-white" /> : 'Accéder au système'}
          </button>
        </form>

        <div className="w-full mt-6 pt-6 border-t border-white/10 flex flex-col items-center">
            <p className="text-muted text-sm mb-3">Vous êtes un patient ?</p>
            <button 
                onClick={() => navigate('/book')}
                className="w-full py-3 rounded-xl font-bold text-white bg-slate-800/80 hover:bg-slate-700 transition-all border border-white/10 hover:border-primary/50 flex items-center justify-center gap-2"
            >
                Prendre un rendez-vous <Activity size={18} className="text-primary" />
            </button>
        </div>
        
        <div className="mt-8 flex justify-center items-center gap-2 text-xs font-bold text-muted" style={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          <ShieldCheck size={16} className="text-success" /> Chiffré de bout-en-bout
        </div>
      </div>
      
      {/* Fallback to ensure gradient looks correct over dark bg */}
      <style>{`
        .bg-blob-1, .bg-blob-2, .bg-blob-3 {
           mix-blend-mode: screen;
        }
      `}</style>
    </div>
  );
};

export default Login;
