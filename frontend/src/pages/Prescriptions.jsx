import React, { useState, useEffect, useMemo } from 'react';
import { createPortal } from 'react-dom';
import api from '../services/api';
import useToastStore from '../store/useToastStore';
import { FileText, Download, Plus, Edit, Trash2, Copy, X, Search, FileSignature } from 'lucide-react';
import Spinner from '../components/Spinner';
import useAuthStore from '../store/useAuthStore';

const Prescriptions = () => {
  const [prescriptions, setPrescriptions] = useState([]);
  const [consultations, setConsultations] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuthStore();
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [selectedPrescription, setSelectedPrescription] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const [currentPage, setCurrentPage] = useState(1);
  const ITEMS_PER_PAGE = 6;
  
  const { addToast } = useToastStore();

  const initialForm = {
    consultation: '', medications: '', dosage: '', posology: '', duration: '', recommendations: ''
  };
  const [formData, setFormData] = useState(initialForm);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [resPres, resCons] = await Promise.all([
        api.get('/prescriptions/'),
        api.get('/consultations/')
      ]);
      setPrescriptions(resPres.data);
      setConsultations(resCons.data);
    } catch (err) {
      console.error(err);
      addToast('Erreur', 'Impossible de charger les ordonnances', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const openNewModal = () => {
    setFormData(initialForm);
    setIsEditMode(false);
    setIsModalOpen(true);
  };

  const handleEditClick = (p) => {
    setSelectedPrescription(p);
    setFormData({
      consultation: p.consultation,
      medications: p.medications || '',
      dosage: p.dosage || '',
      posology: p.posology || '',
      duration: p.duration || '',
      recommendations: p.recommendations || ''
    });
    setIsEditMode(true);
    setIsModalOpen(true);
  };

  const handleDuplicateClick = (p) => {
    setFormData({
      consultation: p.consultation,
      medications: p.medications || '',
      dosage: p.dosage || '',
      posology: p.posology || '',
      duration: p.duration || '',
      recommendations: p.recommendations || ''
    });
    setIsEditMode(false); 
    setIsModalOpen(true);
  };

  const handleDelete = async (id) => {
    if(window.confirm("Êtes-vous sûr de vouloir supprimer cette ordonnance ?")) {
      try {
        await api.delete(`/prescriptions/${id}/`);
        addToast('Supprimé', 'Ordonnance supprimée avec succès', 'success');
        fetchData();
      } catch (err) {
        console.error(err);
        addToast('Erreur', 'Impossible de la supprimer', 'error');
      }
    }
  };

  const handleSaveSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isEditMode && selectedPrescription) {
        await api.put(`/prescriptions/${selectedPrescription.id}/`, formData);
        addToast('Succès', 'Ordonnance mise à jour avec succès.', 'success');
      } else {
        await api.post('/prescriptions/', formData);
        addToast('Succès', 'Ordonnance créée avec succès.', 'success');
      }
      setIsModalOpen(false);
      fetchData();
    } catch (err) {
      console.error(err);
      addToast('Erreur', "L'enregistrement a échoué (vérifiez les champs ou l'unicité de la consult)", 'error');
    }
  };

  const handleDownload = async (id) => {
    try {
      addToast('Téléchargement', 'Génération PDF en cours...', 'info', 1500);
      const response = await api.get(`/prescriptions/${id}/export-pdf/`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Ordonnance_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch(err) {
      console.error(err);
      addToast('Erreur', "Échec de génération PDF", 'error');
    }
  };

  const filteredPrescriptions = useMemo(() => {
    if (!searchQuery) return prescriptions;
    const lowerQ = searchQuery.toLowerCase();
    return prescriptions.filter(p => {
      const meds = (p.medications || '').toLowerCase();
      const poso = (p.posology || '').toLowerCase();
      const rId = String(p.id);
      const cId = String(p.consultation);
      const pd = p.consultation_details?.appointment_details?.patient_details;
      const pName = pd ? `${pd.first_name} ${pd.last_name}`.toLowerCase() : '';
      return meds.includes(lowerQ) || poso.includes(lowerQ) || rId.includes(lowerQ) || cId.includes(lowerQ) || pName.includes(lowerQ);
    });
  }, [prescriptions, searchQuery]);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, prescriptions]);

  return (
    <div className="animate-fade-in">
      <div className="flex justify-between items-center mb-8">
        <div>
           <h1 className="text-3xl font-bold text-main m-0 tracking-tight">Espace Ordonnances</h1>
           <p className="text-muted mt-1">Rédigez, modifiez et téléchargez vos prescriptions PDF.</p>
        </div>
        {user?.role !== 'SECRETARY' && (
          <button onClick={openNewModal} className="btn btn-primary"><Plus size={18} /> Créer une Ordonnance</button>
        )}
      </div>

      <div className="card mb-6 p-4">
        <form onSubmit={e => e.preventDefault()} className="flex w-full">
          <div className="relative w-full max-w-lg">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search size={18} className="text-light" />
            </div>
            <input 
              type="text" 
              className="input pl-10" 
              placeholder="Rechercher médicament ou patient..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </form>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full h-40 flex items-center justify-center"><Spinner size={40} /></div>
        ) : filteredPrescriptions.length === 0 ? (
          <div className="col-span-full p-12 text-center text-muted card bg-transparent border-dashed">
             <FileSignature size={64} className="mx-auto mb-4 opacity-20 text-primary" />
             <p className="text-lg m-0">La base d'ordonnances est vide ou aucune ne correspond.</p>
          </div>
        ) : (
          filteredPrescriptions.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE).map(p => (
            <div key={p.id} className="card flex flex-col justify-between border-t-4 border-t-secondary p-5 hover:shadow-lg transition">
              <div>
                <div className="flex justify-between items-start mb-4">
                  <div>
                     <h3 className="text-lg font-bold text-main m-0 mb-1 flex items-center gap-2">
                        <FileText size={18} className="text-secondary" /> Ordonnance #{p.id}
                     </h3>
                     <p className="text-xs text-muted m-0 font-medium">Liée à la Consult #{p.consultation}</p>
                     
                     {p?.consultation_details?.appointment_details?.patient_details && (
                        <div className="mt-2 flex flex-wrap gap-2">
                           <span className="badge bg-primary-light text-primary border border-primary/20">
                             Patient: {p?.consultation_details?.appointment_details?.patient_details?.first_name} {p?.consultation_details?.appointment_details?.patient_details?.last_name}
                           </span>
                           {p?.consultation_details?.appointment_details?.doctor_details && (
                             <span className="badge bg-secondary-light text-secondary border border-secondary/20">
                               Dr. {p?.consultation_details?.appointment_details?.doctor_details?.last_name}
                             </span>
                           )}
                        </div>
                     )}
                  </div>
                  {user?.role !== 'SECRETARY' && (
                    <div className="flex gap-1 bg-hover p-1 rounded-lg">
                      <button className="btn btn-icon bg-white shadow-sm border border-color hover:text-primary text-muted w-8 h-8 p-0" onClick={() => handleDuplicateClick(p)} title="Dupliquer"><Copy size={14}/></button>
                      <button className="btn btn-icon bg-white shadow-sm border border-color hover:text-primary text-muted w-8 h-8 p-0" onClick={() => handleEditClick(p)} title="Modifier"><Edit size={14}/></button>
                      <button className="btn btn-icon bg-white shadow-sm border border-color hover:text-danger text-muted w-8 h-8 p-0" onClick={() => handleDelete(p.id)} title="Supprimer"><Trash2 size={14}/></button>
                    </div>
                  )}
                </div>
                
                <div className="mb-4">
                  <span className="text-xs font-bold text-light uppercase tracking-wider block mb-2">Traitements Prescrits</span>
                  <div className="bg-main p-3 rounded-lg border border-color text-sm text-main whitespace-pre-wrap max-h-32 overflow-y-auto leading-relaxed shadow-inner">
                    {p.medications}
                  </div>
                </div>
                
                <div className="flex justify-between items-center mb-6 bg-hover rounded-md p-2 px-3 border border-color/50">
                  <span className="text-sm font-semibold text-muted">Durée prescrite:</span>
                  <span className="badge bg-white shadow-sm font-bold text-main">{p.duration}</span>
                </div>
              </div>
              
              <button 
                onClick={() => handleDownload(p.id)} 
                className="btn btn-primary w-full bg-secondary hover:bg-secondary-hover border-transparent"
              >
                <Download size={18} /> Télécharger PDF Sécurisé
              </button>
            </div>
          ))
        )}
      </div>

      {filteredPrescriptions.length > ITEMS_PER_PAGE && (
        <div className="flex justify-between items-center p-4 bg-white border border-color rounded-xl mt-6 shadow-sm">
          <span className="text-sm text-light font-medium">
            Affiche {(currentPage - 1) * ITEMS_PER_PAGE + 1} à {Math.min(currentPage * ITEMS_PER_PAGE, filteredPrescriptions.length)} sur {filteredPrescriptions.length}
          </span>
          <div className="flex gap-2">
            <button 
              className="btn btn-outline py-1 px-3 text-sm bg-hover" 
              disabled={currentPage === 1} 
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
            >
              Précédent
            </button>
            {[...Array(Math.ceil(filteredPrescriptions.length / ITEMS_PER_PAGE))].map((_, i) => (
              <button 
                key={i} 
                className={`btn py-1 px-3 text-sm ${currentPage === i + 1 ? 'btn-primary bg-secondary border-transparent' : 'btn-outline bg-hover'}`} 
                onClick={() => setCurrentPage(i + 1)} 
              >
                {i + 1}
              </button>
            ))}
            <button 
              className="btn btn-outline py-1 px-3 text-sm bg-hover" 
              disabled={currentPage === Math.ceil(filteredPrescriptions.length / ITEMS_PER_PAGE) || Math.ceil(filteredPrescriptions.length / ITEMS_PER_PAGE) === 0} 
              onClick={() => setCurrentPage(prev => prev + 1)}
            >
              Suivant
            </button>
          </div>
        </div>
      )}

      {/* Prescription Form Modal */}
      {isModalOpen && createPortal(
        <div className="modal-overlay">
          <div className="modal-content card max-w-2xl p-0">
            <div className="modal-header p-6 pb-4 bg-hover border-b border-color rounded-t-lg">
              <button onClick={() => setIsModalOpen(false)} className="modal-close"><X size={20} /></button>
              <h2 className="modal-title font-bold text-xl flex items-center gap-2 text-main">
                 <FileSignature className="text-secondary" /> {isEditMode ? 'Modifier Ordonnance' : 'Créer une Ordonnance'}
              </h2>
            </div>
            
            <form onSubmit={handleSaveSubmit} className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 100px)' }}>
              
              <div className="mb-6">
                <label className="label text-main">Consultation Associée *</label>
                <select className="input" required value={formData.consultation} onChange={e => setFormData({...formData, consultation: e.target.value})}>
                  <option value="">-- Sélectionner la consultation --</option>
                  {consultations.map(c => (
                    <option key={c.id} value={c.id}>
                      Consult #{c.id} - Date: {new Date(c.created_at).toLocaleDateString()} (Diagnostic: {c.diagnosis || 'N/A'})
                    </option>
                  ))}
                </select>
                <p className="text-xs text-muted mt-2 m-0 bg-hover p-2 rounded inline-block">
                  L'ordonnance doit être rattachée à une consultation clôturée.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="label">Médicaments (Ligne par ligne) *</label>
                  <textarea className="input" required rows="4" value={formData.medications} onChange={e => setFormData({...formData, medications: e.target.value})} placeholder="Doliprane 1000mg..."></textarea>
                </div>
                <div>
                  <label className="label">Dosage correspondant *</label>
                  <textarea className="input" required rows="4" value={formData.dosage} onChange={e => setFormData({...formData, dosage: e.target.value})} placeholder="1 boîte..."></textarea>
                </div>
              </div>

              <div className="mb-4">
                <label className="label">Posologie détaillée *</label>
                <textarea className="input" required rows="3" value={formData.posology} onChange={e => setFormData({...formData, posology: e.target.value})} placeholder="Prendre avec un grand verre d'eau au cours des repas..."></textarea>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="label">Durée du traitement *</label>
                  <input type="text" className="input" required value={formData.duration} onChange={e => setFormData({...formData, duration: e.target.value})} placeholder="ex: 7 jours" />
                </div>
              </div>

              <div className="mb-6">
                <label className="label">Recommandations (Optionnel)</label>
                <textarea className="input" rows="2" value={formData.recommendations} onChange={e => setFormData({...formData, recommendations: e.target.value})} placeholder="Repos strict, éviter le soleil..."></textarea>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-color mt-2 sticky bottom-0 z-10 bg-white" style={{ background: 'rgba(255, 255, 255, 0.85)', backdropFilter: 'blur(12px)', margin: '0 -1.5rem -1.5rem -1.5rem', padding: '1rem 1.5rem' }}>
                <button type="button" className="btn btn-outline" onClick={() => setIsModalOpen(false)}>Annuler</button>
                <button type="submit" className="btn btn-primary bg-secondary hover:bg-secondary-hover border-transparent px-8">
                  {isEditMode ? 'Enregistrer' : 'Générer Ordonnance'}
                </button>
              </div>
            </form>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
};

export default Prescriptions;
