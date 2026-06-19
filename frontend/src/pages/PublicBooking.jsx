import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, Clock, User, CheckCircle, ChevronRight, ChevronLeft, ArrowLeft, HeartPulse, MapPin } from 'lucide-react';
import useToastStore from '../store/useToastStore';
import axios from 'axios';
import Spinner from '../components/Spinner';

// Assuming base URL for API is http://localhost:8000
// Note: We might want to use a configured Axios instance if available, but for public route a direct call or config is fine.
const API_URL = 'http://localhost:8000/api';

const PublicBooking = () => {
  const navigate = useNavigate();
  const { addToast } = useToastStore();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [doctors, setDoctors] = useState([]);
  const [availableTimes, setAvailableTimes] = useState([]);
  const [loadingTimes, setLoadingTimes] = useState(false);
  
  const [formData, setFormData] = useState({
    doctor_id: '',
    date: '',
    time: '',
    reason: 'Consultation médicale',
    cin: '',
    first_name: '',
    last_name: '',
    phone: '',
    gender: 'O',
    date_of_birth: '2000-01-01'
  });

  // Fetch doctors on mount
  useEffect(() => {
    const fetchDoctors = async () => {
      try {
        const response = await axios.get(`${API_URL}/appointments/public/doctors/`);
        setDoctors(response.data);
      } catch (error) {
        console.error("Error fetching doctors", error);
      }
    };
    fetchDoctors();
  }, []);

  const handleNext = () => setStep((prev) => Math.min(prev + 1, 4));
  const handlePrev = () => setStep((prev) => Math.max(prev - 1, 1));

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleDoctorSelect = (id) => {
    setFormData({ ...formData, doctor_id: id });
    handleNext();
  };

  const submitBooking = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_URL}/appointments/public/book/`, formData);
      setLoading(false);
      handleNext(); // Move to success step
    } catch (error) {
      setLoading(false);
      addToast('Erreur', error.response?.data?.error || 'Une erreur est survenue lors de la réservation.', 'error');
    }
  };

  // Fetch available times when date or doctor changes
  useEffect(() => {
    const fetchTimes = async () => {
      if (formData.date && formData.doctor_id) {
        setLoadingTimes(true);
        // Reset previously selected time if we are fetching new ones
        setFormData(prev => ({ ...prev, time: '' }));
        try {
          const response = await axios.get(`${API_URL}/appointments/public/available-slots/?doctor_id=${formData.doctor_id}&date=${formData.date}`);
          setAvailableTimes(response.data);
        } catch (error) {
          console.error("Error fetching times", error);
          setAvailableTimes([]);
        } finally {
          setLoadingTimes(false);
        }
      } else {
        setAvailableTimes([]);
      }
    };
    fetchTimes();
  }, [formData.date, formData.doctor_id]);

  return (
    <div 
      className="relative flex items-center justify-center overflow-hidden min-h-screen w-full"
      style={{ backgroundColor: '#0f172a' }}
    >
      {/* Animated Background Blobs (Reused from Login) */}
      <div className="bg-blob bg-blob-1"></div>
      <div className="bg-blob bg-blob-2"></div>
      <div className="bg-blob bg-blob-3"></div>
      
      <style>{`
        .bg-blob-1, .bg-blob-2, .bg-blob-3 { mix-blend-mode: screen; }
        .step-indicator {
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .time-slot:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(37,99,235,0.2);
        }
        .doctor-card:hover {
            border-color: var(--primary);
            box-shadow: 0 0 20px rgba(37,99,235,0.15);
        }
      `}</style>

      {/* Back Button */}
      <button 
        onClick={() => navigate('/login')}
        className="absolute top-6 left-6 z-20 flex items-center gap-2 text-white/70 hover:text-white transition-colors glass-panel-dark px-4 py-2 hover:bg-white/5"
        style={{ borderRadius: '2rem' }}
      >
        <ArrowLeft size={18} /> Retour à l'accueil
      </button>

      <div 
        className="glass-panel-dark relative z-10 animate-slide-up flex flex-col w-full"
        style={{ maxWidth: '800px', padding: '0', margin: '2rem', borderRadius: '1.5rem', overflow: 'hidden' }}
      >
        {/* Header section */}
        <div className="p-8 text-center" style={{ background: 'linear-gradient(to right, rgba(15,23,42,0.8), rgba(30,41,59,0.8))', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
          <div className="flex justify-center mb-4">
             <div className="p-3" style={{ background: 'rgba(37,99,235,0.2)', borderRadius: '50%' }}>
                <HeartPulse size={32} className="text-primary" />
             </div>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Prendre un rendez-vous</h1>
          <p className="text-muted">Réservez votre consultation en quelques clics</p>
          
          {/* Progress Bar */}
          <div className="flex items-center justify-between mt-8 relative px-4">
            <div className="absolute top-1/2 left-0 right-0 h-1 bg-white/10 -z-10" style={{ transform: 'translateY(-50%)' }}></div>
            <div 
                className="absolute top-1/2 left-0 h-1 bg-primary -z-10 transition-all duration-500" 
                style={{ transform: 'translateY(-50%)', width: `${((step - 1) / 3) * 100}%` }}
            ></div>
            
            {[1, 2, 3, 4].map((i) => (
              <div 
                key={i} 
                className={`step-indicator flex items-center justify-center w-10 h-10 rounded-full font-bold ${step >= i ? 'bg-primary text-white shadow-[0_0_15px_rgba(37,99,235,0.5)]' : 'bg-slate-800 text-slate-400 border border-white/10'}`}
              >
                {step > i ? <CheckCircle size={20} /> : i}
              </div>
            ))}
          </div>
        </div>

        {/* Content Section */}
        <div className="p-8">
            
            {/* STEP 1: CHOOSE DOCTOR */}
            {step === 1 && (
              <div className="animate-fade-in">
                <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                    <User className="text-primary" /> Choisissez un médecin
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {doctors.map(doctor => (
                        <div 
                            key={doctor.id} 
                            onClick={() => handleDoctorSelect(doctor.id)}
                            className={`doctor-card p-5 rounded-xl cursor-pointer transition-all border ${formData.doctor_id === doctor.id ? 'border-primary bg-primary/20 shadow-[0_0_20px_rgba(37,99,235,0.2)]' : 'border-white/10 bg-white/5 hover:bg-white/10'}`}
                        >
                            <div className="flex items-center gap-4">
                                <div className="w-14 h-14 rounded-full bg-slate-700 flex items-center justify-center text-xl font-bold text-white">
                                    {doctor.first_name[0]}{doctor.last_name[0]}
                                </div>
                                <div>
                                    <h4 className="text-lg font-bold text-white">Dr. {doctor.first_name} {doctor.last_name}</h4>
                                    <p className="text-sm text-primary font-medium">{doctor.specialty}</p>
                                </div>
                            </div>
                        </div>
                    ))}
                    {doctors.length === 0 && (
                        <p className="text-muted col-span-2 text-center py-8">Chargement des médecins...</p>
                    )}
                </div>
              </div>
            )}

            {/* STEP 2: CHOOSE DATE & TIME */}
            {step === 2 && (
              <div className="animate-fade-in">
                 <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                    <Calendar className="text-primary" /> Date et Heure
                 </h3>
                 
                 <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Sélectionnez une date</label>
                        <input 
                            type="date" 
                            name="date"
                            value={formData.date}
                            onChange={handleChange}
                            min={new Date().toISOString().split('T')[0]}
                            className="w-full bg-slate-800/50 border border-white/10 rounded-xl p-4 text-white focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
                        />
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Créneaux disponibles</label>
                        {!formData.date ? (
                            <div className="h-full flex items-center justify-center p-6 bg-slate-800/30 rounded-xl border border-white/5 border-dashed text-muted text-center text-sm min-h-[160px]">
                                Veuillez sélectionner une date pour voir les créneaux.
                            </div>
                        ) : loadingTimes ? (
                            <div className="h-full flex items-center justify-center p-6 bg-slate-800/30 rounded-xl border border-white/5 border-dashed text-primary text-center text-sm flex-col gap-3 min-h-[160px]">
                                <Spinner size={24} />
                                <span className="animate-pulse">Recherche des disponibilités...</span>
                            </div>
                        ) : availableTimes.length > 0 ? (
                            <div className="grid grid-cols-3 gap-3">
                                {availableTimes.map(time => (
                                    <button
                                        key={time}
                                        onClick={() => setFormData({...formData, time})}
                                        className={`time-slot py-3 rounded-lg font-medium transition-all ${formData.time === time ? 'bg-primary text-white shadow-[0_0_15px_rgba(37,99,235,0.6)] border border-primary' : 'bg-slate-800/50 text-slate-300 hover:bg-slate-700 hover:text-white border border-white/10 hover:border-primary/50 shadow-sm hover:shadow-md'}`}
                                    >
                                        {time}
                                    </button>
                                ))}
                            </div>
                        ) : (
                            <div className="h-full flex items-center justify-center p-6 bg-rose-500/10 rounded-xl border border-rose-500/20 text-rose-400 text-center text-sm flex-col gap-2 shadow-[0_0_20px_rgba(244,63,94,0.1)] min-h-[160px]">
                                <span className="text-xl">⚠️</span>
                                <strong>Journée complète</strong>
                                <span className="text-xs opacity-80">Aucun créneau disponible pour ce médecin à cette date. Veuillez choisir une autre date.</span>
                            </div>
                        )}
                    </div>
                 </div>

                 <div className="mt-8 flex justify-between">
                    <button onClick={handlePrev} className="px-6 py-3 rounded-xl font-medium text-white bg-slate-800 hover:bg-slate-700 transition-colors flex items-center gap-2">
                        <ChevronLeft size={20} /> Précédent
                    </button>
                    <button 
                        onClick={handleNext} 
                        disabled={!formData.date || !formData.time}
                        className={`px-8 py-3 rounded-xl font-bold text-white transition-all flex items-center gap-2 ${(!formData.date || !formData.time) ? 'bg-slate-700 opacity-50 cursor-not-allowed' : 'bg-primary hover:bg-blue-600 shadow-[0_0_20px_rgba(37,99,235,0.4)]'}`}
                    >
                        Continuer <ChevronRight size={20} />
                    </button>
                 </div>
              </div>
            )}

            {/* STEP 3: PATIENT INFO */}
            {step === 3 && (
              <div className="animate-fade-in">
                 <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                    <User className="text-primary" /> Vos informations
                 </h3>
                 
                 <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div>
                        <label className="block text-xs font-semibold text-slate-400 mb-1 uppercase tracking-wider">Numéro CIN *</label>
                        <input type="text" name="cin" value={formData.cin} onChange={handleChange} required placeholder="Ex: AB123456" className="w-full bg-slate-800/50 border border-white/10 rounded-xl p-3.5 text-white focus:border-primary outline-none" />
                    </div>
                    <div>
                        <label className="block text-xs font-semibold text-slate-400 mb-1 uppercase tracking-wider">Téléphone *</label>
                        <input type="tel" name="phone" value={formData.phone} onChange={handleChange} required placeholder="0600000000" className="w-full bg-slate-800/50 border border-white/10 rounded-xl p-3.5 text-white focus:border-primary outline-none" />
                    </div>
                    <div>
                        <label className="block text-xs font-semibold text-slate-400 mb-1 uppercase tracking-wider">Prénom *</label>
                        <input type="text" name="first_name" value={formData.first_name} onChange={handleChange} required placeholder="Votre prénom" className="w-full bg-slate-800/50 border border-white/10 rounded-xl p-3.5 text-white focus:border-primary outline-none" />
                    </div>
                    <div>
                        <label className="block text-xs font-semibold text-slate-400 mb-1 uppercase tracking-wider">Nom *</label>
                        <input type="text" name="last_name" value={formData.last_name} onChange={handleChange} required placeholder="Votre nom" className="w-full bg-slate-800/50 border border-white/10 rounded-xl p-3.5 text-white focus:border-primary outline-none" />
                    </div>
                    <div className="md:col-span-2">
                        <label className="block text-xs font-semibold text-slate-400 mb-1 uppercase tracking-wider">Motif de consultation (Optionnel)</label>
                        <input type="text" name="reason" value={formData.reason} onChange={handleChange} placeholder="Ex: Contrôle de routine" className="w-full bg-slate-800/50 border border-white/10 rounded-xl p-3.5 text-white focus:border-primary outline-none" />
                    </div>
                 </div>

                 <div className="mt-8 flex justify-between">
                    <button onClick={handlePrev} className="px-6 py-3 rounded-xl font-medium text-white bg-slate-800 hover:bg-slate-700 transition-colors flex items-center gap-2">
                        <ChevronLeft size={20} /> Précédent
                    </button>
                    <button 
                        onClick={submitBooking} 
                        disabled={loading || !formData.cin || !formData.first_name || !formData.last_name || !formData.phone}
                        className={`px-8 py-3 rounded-xl font-bold text-white transition-all flex items-center gap-2 ${loading || !formData.cin ? 'bg-slate-700 opacity-50 cursor-not-allowed' : 'bg-emerald-500 hover:bg-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.4)]'}`}
                    >
                        {loading ? <Spinner size={20} /> : 'Confirmer le rendez-vous'} <CheckCircle size={20} />
                    </button>
                 </div>
              </div>
            )}

            {/* STEP 4: SUCCESS */}
            {step === 4 && (
              <div className="animate-fade-in text-center py-8">
                 <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-emerald-500/20 text-emerald-400 mb-6 relative">
                    <div className="absolute inset-0 rounded-full bg-emerald-500/20 animate-ping"></div>
                    <CheckCircle size={48} />
                 </div>
                 <h2 className="text-3xl font-bold text-white mb-4">Rendez-vous Confirmé !</h2>
                 <p className="text-slate-300 text-lg max-w-md mx-auto mb-8">
                    Merci {formData.first_name}. Votre rendez-vous a été enregistré avec succès pour le <strong className="text-white">{formData.date}</strong> à <strong className="text-white">{formData.time}</strong>.
                 </p>
                 
                 <div className="bg-slate-800/50 border border-white/10 rounded-2xl p-6 max-w-sm mx-auto text-left mb-8">
                    <div className="flex items-center gap-3 mb-4">
                        <Calendar className="text-primary" size={20} />
                        <div>
                            <p className="text-xs text-muted font-bold uppercase">Date</p>
                            <p className="text-white font-medium">{formData.date}</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3 mb-4">
                        <Clock className="text-primary" size={20} />
                        <div>
                            <p className="text-xs text-muted font-bold uppercase">Heure</p>
                            <p className="text-white font-medium">{formData.time}</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <MapPin className="text-primary" size={20} />
                        <div>
                            <p className="text-xs text-muted font-bold uppercase">Lieu</p>
                            <p className="text-white font-medium">Clinique MedPredict</p>
                        </div>
                    </div>
                 </div>

                 <button 
                    onClick={() => navigate('/login')}
                    className="btn btn-primary px-8 py-3 text-lg font-bold shadow-[0_0_20px_rgba(37,99,235,0.4)]"
                 >
                    Retour à l'accueil
                 </button>
              </div>
            )}

        </div>
      </div>
    </div>
  );
};

export default PublicBooking;
