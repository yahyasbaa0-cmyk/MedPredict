import React, { useState, useEffect, useMemo } from 'react';
import api from '../services/api';
import useToastStore from '../store/useToastStore';
import { Activity, Beaker, AlertTriangle, CheckCircle, X, Plus, Clock, FileText, ChevronDown, ChevronUp, Trash2, Search } from 'lucide-react';
import Spinner from '../components/Spinner';
import useAuthStore from '../store/useAuthStore';

const Consultations = () => {
  const [symptomsList, setSymptomsList] = useState([]);
  const [currentSymptom, setCurrentSymptom] = useState('');
  const [loading, setLoading] = useState(false);
  const [predictions, setPredictions] = useState(null);
  const [error, setError] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [pastConsultations, setPastConsultations] = useState([]);
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState(user?.role === 'SECRETARY' ? 'HISTORY' : 'NEW'); 
  const [expandedConsult, setExpandedConsult] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const [currentPage, setCurrentPage] = useState(1);
  const ITEMS_PER_PAGE = 8;
  const { addToast } = useToastStore();

  const [formData, setFormData] = useState({
    appointment: '', diagnosis: '', doctor_notes: ''
  });

  const fetchData = async () => {
    try {
      const [resAppts, resCons] = await Promise.all([
        api.get('/appointments/'),
        api.get('/consultations/')
      ]);
      setAppointments(resAppts.data.filter(a => ['PLANNED', 'CONFIRMED', 'COMPLETED'].includes(a.status)));
      setPastConsultations(resCons.data || []);
    } catch (err) {
      console.error(err);
      addToast('Erreur', 'Impossible de charger les données de consultation', 'error');
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAddSymptom = (e) => {
    e.preventDefault();
    const cleanSymp = currentSymptom.trim().toLowerCase();
    if (cleanSymp && !symptomsList.includes(cleanSymp)) {
      setSymptomsList([...symptomsList, cleanSymp]);
      setCurrentSymptom('');
    }
  };

  const removeSymptom = (sympToRemove) => {
    setSymptomsList(symptomsList.filter(s => s !== sympToRemove));
  };

  const handlePredict = async () => {
    if (symptomsList.length === 0) return;
    
    setLoading(true);
    setError(null);
    try {
      const res = await api.post('/consultations/analyze-symptoms/', { symptoms: symptomsList });
      setPredictions(res.data);
      addToast('IA Prête', 'Les recommandations ont été générées', 'success');
    } catch (err) {
      console.error(err);
      setError("Le service d'assistance IA est actuellement indisponible.");
      addToast('Erreur IA', "L'API IA est indisponible", 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveConsultation = async () => {
    try {
      await api.post('/consultations/', {
        appointment: formData.appointment,
        symptoms: symptomsList.length > 0 ? symptomsList.join(', ') : 'Aucun symptôme spécifié',
        diagnosis: formData.diagnosis,
        doctor_notes: formData.doctor_notes,
        ai_suggestions: predictions || {}
      });
      addToast('Succès', "Consultation enregistrée avec succès !", 'success');
      setFormData({appointment: '', diagnosis: '', doctor_notes: ''});
      setSymptomsList([]);
      setPredictions(null);
      fetchData();
      setActiveTab('HISTORY');
    } catch(e) {
      console.error(e);
      addToast('Erreur', "Vérifiez que ce RDV n'a pas déjà de consultation.", 'error');
    }
  };

  const handleDeleteConsultation = async (e, id) => {
    e.stopPropagation();
    if(window.confirm("Êtes-vous sûr de vouloir supprimer définitivement cette consultation ? Attention : cela supprimera peut-être l'ordonnance associée si elle existe !")) {
      try {
        await api.delete(`/consultations/${id}/`);
        addToast('Supprimé', "Consultation supprimée de l'historique", 'success');
        fetchData();
      } catch (err) {
        console.error(err);
        addToast('Erreur', "Impossible de supprimer la consultation.", 'error');
      }
    }
  };

  const filteredConsultations = useMemo(() => {
    if (!searchQuery) return pastConsultations;
    const lowerQ = searchQuery.toLowerCase();
    return pastConsultations.filter(c => {
      const diag = (c.diagnosis || '').toLowerCase();
      const symp = (c.symptoms || '').toLowerCase();
      const notes = (c.doctor_notes || '').toLowerCase();
      const pName = c.appointment_details?.patient_details ? `${c.appointment_details.patient_details.first_name} ${c.appointment_details.patient_details.last_name}`.toLowerCase() : '';
      return diag.includes(lowerQ) || symp.includes(lowerQ) || notes.includes(lowerQ) || pName.includes(lowerQ);
    });
  }, [pastConsultations, searchQuery]);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, pastConsultations]);

  return (
    <div className="animate-fade-in">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-main m-0 tracking-tight">Espace Consultations</h1>
          <p className="text-muted mt-1">Saisie médicale et assistance IA.</p>
        </div>
        <div className="flex bg-hover p-1 rounded-lg border border-color">
           <button className={`btn shadow-none border-transparent py-1 px-4 ${activeTab === 'HISTORY' ? 'bg-white text-primary shadow-sm' : 'bg-transparent text-muted hover:text-main'}`} onClick={() => setActiveTab('HISTORY')}>
             <Clock size={16}/> Historique
           </button>
           {user?.role !== 'SECRETARY' && (
             <button className={`btn shadow-none border-transparent py-1 px-4 ${activeTab === 'NEW' ? 'bg-white text-primary shadow-sm' : 'bg-transparent text-muted hover:text-main'}`} onClick={() => setActiveTab('NEW')}>
               <Plus size={16}/> Nouvelle
             </button>
           )}
        </div>
      </div>
      
      {activeTab === 'NEW' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="card shadow-sm">
            <h2 className="text-xl font-bold text-main mb-6 border-b border-color pb-4">Dossier Clinique</h2>
            <form className="flex flex-col gap-6">
              <div>
                <label className="label">Sélectionner le Rendez-vous *</label>
                <select className="input" value={formData.appointment} onChange={e => setFormData({...formData, appointment: e.target.value})}>
                  <option value="">-- Choisir un rendez-vous en attente --</option>
                  {appointments.map(a => (
                    <option key={a.id} value={a.id}>
                      {a.date} - {a.patient_details ? `${a.patient_details.first_name} ${a.patient_details.last_name}` : `P #${a.patient}`} ({a.reason})
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="label flex justify-between items-end">
                  <span>Symptômes observés</span>
                  <span className="text-xs font-normal text-primary bg-primary-light px-2 py-0.5 rounded-full">Anglais requis pour l'IA</span>
                </label>
                <div className="flex gap-2 mb-3">
                  <input 
                    type="text" 
                    className="input bg-hover" 
                    placeholder="ex: fever, cough..."
                    value={currentSymptom}
                    onChange={e => setCurrentSymptom(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') handleAddSymptom(e) }}
                  />
                  <button type="button" className="btn btn-outline border-border-color" onClick={handleAddSymptom}><Plus size={18}/></button>
                </div>
                <div className="flex flex-wrap gap-2 min-h-[40px] p-3 bg-main rounded-md border border-color border-dashed">
                  {symptomsList.map((s, idx) => (
                    <span key={idx} className="badge badge-primary bg-white border border-primary px-3 py-1 flex items-center gap-2">
                      {s}
                      <X size={14} className="cursor-pointer hover:text-danger hover:scale-110 transition" onClick={() => removeSymptom(s)} />
                    </span>
                  ))}
                  {symptomsList.length === 0 && <span className="text-sm text-light italic m-auto">Aucun symptôme ajouté.</span>}
                </div>
              </div>
              
              <button 
                type="button" 
                className="btn w-fit" 
                style={{ backgroundColor: '#8b5cf6', color: 'white', boxShadow: '0 4px 14px 0 rgba(139, 92, 246, 0.39)' }} 
                onClick={handlePredict} 
                disabled={loading || symptomsList.length === 0}
              >
                {loading ? <Spinner size={18} className="text-white"/> : <Beaker size={18} />} 
                {loading ? 'Analyse...' : "Solliciter l'IA Médicale"}
              </button>
              
              <div className="w-full h-px bg-border-color my-2"></div>
              
              <div>
                <label className="label">Diagnostic Médical Validé *</label>
                <input type="text" className="input" placeholder="Saisissez le diagnostic définitif" value={formData.diagnosis} onChange={e => setFormData({...formData, diagnosis: e.target.value})}/>
              </div>
              <div>
                <label className="label">Notes & Observations (Facultatif)</label>
                <textarea className="input" rows="4" placeholder="Description de l'examen clinique, constantes..." value={formData.doctor_notes} onChange={e => setFormData({...formData, doctor_notes: e.target.value})}></textarea>
              </div>
              
              <div className="flex justify-end pt-4">
                <button type="button" className="btn btn-primary px-8" onClick={handleSaveConsultation} disabled={!formData.appointment || !formData.diagnosis}>
                  Enregistrer et Clôturer
                </button>
              </div>
            </form>
          </div>

          {/* Panel IA */}
          <div className="card shadow-sm border-2 border-dashed border-[#c4b5fd] bg-[#fdfcff] flex flex-col">
            <div className="flex items-center gap-3 mb-6 border-b border-[#ede9fe] pb-4">
              <div className="p-2 bg-[#f3e8ff] rounded-lg"><Activity color="#8b5cf6" size={24} /></div>
              <h2 className="text-xl font-bold m-0" style={{ color: '#8b5cf6' }}>MedAI Assistant</h2>
            </div>
            
            <div className="bg-warning-light p-4 rounded-lg flex items-start gap-3 mb-6">
              <AlertTriangle size={20} className="text-warning shrink-0 mt-0.5" />
              <p className="text-sm text-warning m-0 leading-relaxed font-medium">
                Cet outil fournit une aide basée sur le Machine Learning. <strong>Il ne remplace en aucun cas le jugement et l'expertise du médecin.</strong>
              </p>
            </div>

            {error && (
              <div className="bg-danger-light text-danger p-4 rounded-lg text-center font-medium mb-4">
                {error}
              </div>
            )}

            <div className="flex-1 flex flex-col">
              {!predictions && !error && !loading && (
                <div className="m-auto text-center p-8 flex flex-col items-center opacity-60">
                    <Activity size={64} className="text-[#8b5cf6] mb-4" />
                    <p className="text-[#8b5cf6] font-medium m-0">Saisissez les symptômes à gauche et cliquez sur analyser pour voir les suggestions.</p>
                </div>
              )}

              {predictions && predictions.predictions && predictions.predictions.length > 0 && (
                <div className="animate-fade-in">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-muted mb-4">Diagnostics Probables</h3>
                  <div className="flex flex-col gap-3">
                    {predictions.predictions.map((p, idx) => {
                      let confidenceColor = '#ef4444'; 
                      let bgHint = 'bg-danger-light';
                      if (p.confidence >= 80) { confidenceColor = '#10b981'; bgHint = 'bg-success-light'; }
                      else if (p.confidence >= 50) { confidenceColor = '#f59e0b'; bgHint = 'bg-warning-light'; }

                      return (
                        <div key={idx} className="bg-white p-4 rounded-xl border border-color shadow-sm flex justify-between items-center transition hover:shadow-md">
                          <div className="flex items-center gap-3">
                            <div className={`p-2 rounded-full ${bgHint}`}>
                              {idx === 0 ? <CheckCircle size={20} color={confidenceColor} /> : <Activity size={20} color={confidenceColor} />}
                            </div>
                            <span className="font-bold text-main text-lg capitalize">{p.disease.replace(/_/g, ' ')}</span>
                          </div>
                          <div className="text-right">
                            <div className="font-black text-2xl" style={{ color: confidenceColor }}>
                              {p.confidence}%
                            </div>
                            <div className="text-xs font-semibold text-muted tracking-wide uppercase">Confiance</div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
              
              {predictions && predictions.predictions && predictions.predictions.length === 0 && (
                <div className="m-auto text-center p-8 bg-white rounded-xl border border-color shadow-sm">
                  <p className="text-muted m-0 font-medium">Aucun diagnostic clair identifié pour ces symptômes.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'HISTORY' && (
         <div className="card p-0 overflow-hidden bg-main">
            <div className="p-4 bg-white border-b border-color">
              <div className="relative max-w-md w-full">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search size={18} className="text-light" />
                </div>
                <input 
                  type="text" 
                  className="input pl-10" 
                  placeholder="Rechercher par diagnostic, symptômes..." 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>
           
            <div className="bg-white">
              {filteredConsultations.length === 0 ? (
                <div className="p-12 text-center text-muted">
                  <FileText size={48} className="mx-auto mb-4 opacity-20 text-primary" />
                  <p className="text-lg m-0">Aucune consultation passée enregistrée.</p>
                </div>
              ) : (
                <div className="flex flex-col">
                  {filteredConsultations.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE).map(c => (
                    <div key={c.id} className="border-b last:border-b-0 border-color animate-fade-in group">
                      <div 
                        className={`flex justify-between items-center p-5 cursor-pointer transition ${expandedConsult === c.id ? 'bg-primary-light/50' : 'hover:bg-hover'}`}
                        onClick={() => setExpandedConsult(expandedConsult === c.id ? null : c.id)}
                      >
                        <div className="flex items-center gap-4">
                          <div className="bg-white shadow-sm border border-color p-3 rounded-xl text-primary"><FileText size={20}/></div>
                          <div>
                              <div className="font-bold text-main flex items-center gap-2 mb-1">
                                Séance #{c.id} 
                                {c.appointment_details?.patient_details && (
                                  <span className="badge badge-primary bg-primary text-white border-none">{c.appointment_details.patient_details.first_name} {c.appointment_details.patient_details.last_name}</span>
                                )}
                              </div>
                              <div className="text-sm text-light flex items-center gap-1"><Clock size={12}/> {new Date(c.date).toLocaleString()}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="badge badge-success text-[0.85rem] px-3 py-1 font-bold">{c.diagnosis}</div>
                          <div className="text-muted bg-white p-1 rounded-full shadow-sm border border-color">
                            {expandedConsult === c.id ? <ChevronUp size={16}/> : <ChevronDown size={16}/>}
                          </div>
                          {user?.role !== 'SECRETARY' && (
                            <button 
                              className="btn btn-outline-danger btn-icon ml-2 bg-white opacity-0 group-hover:opacity-100 transition-opacity"
                              onClick={(e) => handleDeleteConsultation(e, c.id)} 
                              title="Supprimer la consultation"
                            >
                              <Trash2 size={16} />
                            </button>
                          )}
                        </div>
                      </div>
                      
                      {expandedConsult === c.id && (
                        <div className="p-6 bg-hover/50 border-t border-color shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)]">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl">
                              <div>
                                <h4 className="text-xs font-bold text-muted uppercase tracking-wider mb-3">Symptômes Déclarés</h4>
                                <div className="flex gap-2 flex-wrap">
                                  {(c.symptoms || 'Non spécifié').split(',').map((s, i) => (
                                    <span key={i} className="badge bg-white text-main border border-color shadow-sm">{s.trim()}</span>
                                  ))}
                                </div>
                              </div>
                              <div>
                                <h4 className="text-xs font-bold text-muted uppercase tracking-wider mb-3">Notes & Observations</h4>
                                <div className="bg-white p-4 rounded-xl border border-color shadow-sm text-sm text-main whitespace-pre-wrap leading-relaxed">
                                  {c.doctor_notes || <span className="text-light italic">Aucune note renseignée</span>}
                                </div>
                              </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
               </div>
              )}
            </div>

            {filteredConsultations.length > ITEMS_PER_PAGE && (
              <div className="flex justify-between items-center p-4 bg-hover border-t border-color">
                <span className="text-sm text-light font-medium">
                  Affiche {(currentPage - 1) * ITEMS_PER_PAGE + 1} à {Math.min(currentPage * ITEMS_PER_PAGE, filteredConsultations.length)} sur {filteredConsultations.length} éléments
                </span>
                <div className="flex gap-2">
                  <button 
                    className="btn btn-outline py-1 px-3 text-sm bg-white" 
                    disabled={currentPage === 1} 
                    onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                  >
                    Précédent
                  </button>
                  {[...Array(Math.ceil(filteredConsultations.length / ITEMS_PER_PAGE))].map((_, i) => (
                    <button 
                      key={i} 
                      className={`btn py-1 px-3 text-sm ${currentPage === i + 1 ? 'btn-primary' : 'btn-outline bg-white'}`} 
                      onClick={() => setCurrentPage(i + 1)} 
                    >
                      {i + 1}
                    </button>
                  ))}
                  <button 
                    className="btn btn-outline py-1 px-3 text-sm bg-white" 
                    disabled={currentPage === Math.ceil(filteredConsultations.length / ITEMS_PER_PAGE) || Math.ceil(filteredConsultations.length / ITEMS_PER_PAGE) === 0} 
                    onClick={() => setCurrentPage(prev => prev + 1)}
                  >
                    Suivant
                  </button>
                </div>
              </div>
            )}
         </div>
      )}
    </div>
  );
};

export default Consultations;
