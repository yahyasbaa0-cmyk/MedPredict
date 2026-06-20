import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import api from '../services/api';
import useToastStore from '../store/useToastStore';
import { Search, Plus, User as UserIcon, X, Edit, Trash2, ShieldAlert } from 'lucide-react';
import Spinner from '../components/Spinner';
import useAuthStore from '../store/useAuthStore';

const Patients = () => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState(null);
  
  const { addToast } = useToastStore();
  const { user } = useAuthStore();

  const [currentPage, setCurrentPage] = useState(1);
  const ITEMS_PER_PAGE = 8;

  const initialForm = {
    first_name: '', last_name: '', date_of_birth: '', gender: 'M',
    phone: '', email: '', blood_group: '', cin: '', city: 'Casablanca',
    allergies: '', medical_history: '', emergency_contact: '', address: ''
  };
  const [formData, setFormData] = useState(initialForm);

  const fetchPatients = async (query = '') => {
    setLoading(true);
    try {
      const res = await api.get(`/patients/?search=${query}`);
      setPatients(res.data);
    } catch (err) {
      console.error(err);
      addToast('Erreur', 'Impossible de charger les dossiers', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  useEffect(() => {
    setCurrentPage(1);
  }, [patients]);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchPatients(search);
  };

  const openNewPatientModal = () => {
    setFormData(initialForm);
    setIsEditMode(false);
    setIsModalOpen(true);
  };

  const handleSaveSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isEditMode && selectedPatient) {
        await api.put(`/patients/${selectedPatient.id}/`, formData);
        addToast('Succès', 'Patient mis à jour avec succès.', 'success');
      } else {
        await api.post('/patients/', formData);
        addToast('Succès', 'Nouveau patient créé avec succès.', 'success');
      }
      setIsModalOpen(false);
      setIsViewModalOpen(false);
      fetchPatients();
    } catch (err) {
      console.error(err);
      if(err.response?.data) {
        addToast('Erreur', 'Vérifiez les champs saisis (le CIN doit être unique).', 'error');
      } else {
        addToast('Erreur', "Erreur lors de l'enregistrement du patient.", 'error');
      }
    }
  };

  const handleOpenPatient = (p) => {
    setSelectedPatient(p);
    setIsViewModalOpen(true);
  };

  const handleEditClick = (p) => {
    setSelectedPatient(p);
    setFormData({
      first_name: p.first_name || '', last_name: p.last_name || '', 
      date_of_birth: p.date_of_birth || '', gender: p.gender || 'M',
      phone: p.phone || '', email: p.email || '', blood_group: p.blood_group || '', 
      cin: p.cin || '', city: p.city || 'Casablanca',
      allergies: p.allergies || '', medical_history: p.medical_history || '',
      emergency_contact: p.emergency_contact || '', address: p.address || ''
    });
    setIsEditMode(true);
    setIsViewModalOpen(false);
    setIsModalOpen(true);
  };

  const handleDeletePatient = async (id) => {
    if(window.confirm("Êtes-vous sûr de vouloir supprimer définitivement ce dossier patient ?")) {
      try {
        await api.delete(`/patients/${id}/`);
        addToast('Supprimé', 'Dossier supprimé avec succès', 'success');
        setIsViewModalOpen(false);
        fetchPatients();
      } catch (err) {
        console.error(err);
        addToast('Erreur', 'Impossible de supprimer le dossier.', 'error');
      }
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="flex justify-between items-center mb-8">
        <div>
           <h1 className="text-3xl font-bold text-main m-0 tracking-tight">Dossiers Patients</h1>
           <p className="text-muted mt-1">Gérez la base de données de vos patients.</p>
        </div>
        <button onClick={openNewPatientModal} className="btn btn-primary"><Plus size={18} /> Nouveau Patient</button>
      </div>

      <div className="card mb-6 p-4">
        <form onSubmit={handleSearch} className="flex gap-4 w-full">
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search size={18} className="text-light" />
            </div>
            <input 
              type="text" 
              className="input pl-10 w-full" 
              placeholder="Rechercher par CIN, nom, prénom ou email..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-secondary px-6">Rechercher</button>
        </form>
      </div>

      <div className="card p-0 overflow-hidden shadow-sm">
        {loading ? (
          <div className="p-8 text-center flex justify-center"><Spinner size={40} /></div>
        ) : patients.length === 0 ? (
          <div className="p-12 text-center text-muted">
             <UserIcon size={64} className="mx-auto mb-4 opacity-20 text-primary" />
             <p className="text-lg">Aucun patient trouvé correspondant à la recherche.</p>
          </div>
        ) : (
          <div className="table-wrapper border-0">
            <table className="table">
              <thead>
                <tr>
                  <th>Nom Complet</th>
                  <th>CIN / Ville</th>
                  <th>Contact</th>
                  <th>Urgence / Santé</th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {patients.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE).map(p => (
                  <tr key={p.id}>
                    <td>
                      <div className="font-semibold text-main text-base">{p.first_name} {p.last_name}</div>
                      <div className="text-sm text-light mt-1">Né(e) le {p.date_of_birth} • {p.gender}</div>
                    </td>
                    <td>
                      <div className="badge badge-primary mb-1">{p.cin || 'N/A'}</div>
                      <div className="text-sm text-muted">{p.city}</div>
                    </td>
                    <td>
                      <div className="text-sm text-main font-medium">{p.phone || '-'}</div>
                      <div className="text-sm text-light mt-1 w-32 truncate" title={p.email || ''}>{p.email || '-'}</div>
                    </td>
                    <td>
                      <div className="flex flex-wrap gap-2">
                         {p.blood_group && <span className="badge badge-danger">{p.blood_group}</span>}
                         {p.allergies && <span className="badge badge-warning" title={p.allergies}>Allergies</span>}
                      </div>
                    </td>
                    <td>
                      <div className="flex justify-end gap-2">
                         <button onClick={() => handleOpenPatient(p)} className="btn btn-outline text-sm py-1 px-3">Dossier</button>
                         <button onClick={() => handleEditClick(p)} className="btn btn-outline-primary btn-icon" title="Modifier"><Edit size={16} /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {patients.length > ITEMS_PER_PAGE && (
          <div className="flex justify-between items-center p-4 bg-hover border-t border-color">
            <span className="text-sm text-light font-medium">
              Affiche {(currentPage - 1) * ITEMS_PER_PAGE + 1} à {Math.min(currentPage * ITEMS_PER_PAGE, patients.length)} sur {patients.length} dossiers
            </span>
            <div className="flex gap-2">
              <button 
                className="btn btn-outline py-1 px-3 text-sm" 
                disabled={currentPage === 1} 
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              >
                Précédent
              </button>
              {[...Array(Math.ceil(patients.length / ITEMS_PER_PAGE))].map((_, i) => (
                <button 
                  key={i} 
                  className={`btn py-1 px-3 text-sm ${currentPage === i + 1 ? 'btn-primary' : 'btn-outline'}`} 
                  onClick={() => setCurrentPage(i + 1)} 
                >
                  {i + 1}
                </button>
              ))}
              <button 
                className="btn btn-outline py-1 px-3 text-sm" 
                disabled={currentPage === Math.ceil(patients.length / ITEMS_PER_PAGE) || Math.ceil(patients.length / ITEMS_PER_PAGE) === 0} 
                onClick={() => setCurrentPage(prev => prev + 1)}
              >
                Suivant
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Patient View Modal */}
      {isViewModalOpen && selectedPatient && createPortal(
        <div className="modal-overlay">
          <div className="modal-content card max-w-2xl p-0">
            <div className="modal-header p-6 pb-4 mb-0 bg-primary-light border-b border-color rounded-t-lg relative">
               <button onClick={() => setIsViewModalOpen(false)} className="modal-close"><X size={20} /></button>
               <div className="flex justify-between items-start pr-8">
                 <div>
                   <h2 className="modal-title text-primary text-2xl font-bold">{selectedPatient.first_name} {selectedPatient.last_name}</h2>
                   <p className="text-muted mt-1 m-0">Dossier Médical Complet</p>
                 </div>
                 <div className="badge badge-primary">{selectedPatient.cin || 'Pas de CIN'}</div>
               </div>
            </div>

            <div className="p-6">
              <div className="grid grid-cols-2 gap-6 mb-6">
                <div className="bg-main p-4 rounded-lg border border-color">
                   <h4 className="text-sm font-bold text-muted uppercase tracking-wider mb-4">Informations Générales</h4>
                   <p className="mb-2 text-sm"><strong className="text-main">Date de naissance:</strong> {selectedPatient.date_of_birth} ({selectedPatient.gender})</p>
                   <p className="mb-2 text-sm"><strong className="text-main">Téléphone:</strong> <span className={selectedPatient.phone ? '' : 'text-light italic'}>{selectedPatient.phone || 'Non renseigné'}</span></p>
                   <p className="mb-2 text-sm"><strong className="text-main">Email:</strong> <span className={selectedPatient.email ? '' : 'text-light italic'}>{selectedPatient.email || 'Non renseigné'}</span></p>
                   <p className="mb-2 text-sm"><strong className="text-main">Ville:</strong> {selectedPatient.city}</p>
                   <p className="text-sm"><strong className="text-main">Adresse:</strong> {selectedPatient.address || '-'}</p>
                </div>

                <div className="bg-danger-light p-4 rounded-lg border border-[#fecdd3]">
                   <h4 className="text-sm font-bold text-danger uppercase tracking-wider mb-4 flex items-center gap-2">
                     <ShieldAlert size={16}/> Santé & Urgences
                   </h4>
                   <p className="mb-2 text-sm"><strong className="text-danger">Groupe Sanguin:</strong> {selectedPatient.blood_group ? <span className="badge badge-danger ml-2">{selectedPatient.blood_group}</span> : '-'}</p>
                   <p className="mb-4 text-sm"><strong className="text-danger">Contact urgence:</strong> {selectedPatient.emergency_contact || 'Non renseigné'}</p>
                   
                   <div className="mb-3">
                     <strong className="block text-xs uppercase text-danger opacity-80 mb-1">Allergies déclarées</strong>
                     <p className="text-sm bg-white p-2 rounded border border-[#ffe4e6] text-[#881337] m-0">
                       {selectedPatient.allergies || 'Aucune allergie connue'}
                     </p>
                   </div>
                   
                   <div>
                     <strong className="block text-xs uppercase text-danger opacity-80 mb-1">Antécédents médicaux</strong>
                     <p className="text-sm bg-white p-2 rounded border border-[#ffe4e6] text-[#881337] m-0">
                       {selectedPatient.medical_history || 'Aucun antécédent particulier'}
                     </p>
                   </div>
                </div>
              </div>

              <div className="flex justify-between items-center border-t border-color pt-6">
                 {user?.role !== 'SECRETARY' && (
                   <button className="btn btn-outline-danger" onClick={() => handleDeletePatient(selectedPatient.id)}>
                     <Trash2 size={16}/> <span className="hidden sm:inline">Supprimer le dossier</span>
                   </button>
                 )}
                 <div className="flex gap-3">
                   <button className="btn btn-outline" onClick={() => setIsViewModalOpen(false)}>Fermer</button>
                   <button className="btn btn-primary" onClick={() => handleEditClick(selectedPatient)}><Edit size={16}/> Modifier</button>
                 </div>
              </div>
            </div>
          </div>
        </div>,
        document.body
      )}

      {/* Patient Create/Edit Form Modal */}
      {isModalOpen && createPortal(
        <div className="modal-overlay">
          <div className="modal-content card max-w-3xl p-0">
            <div className="modal-header p-6 pb-4 bg-hover border-b border-color rounded-t-lg">
              <button onClick={() => setIsModalOpen(false)} className="modal-close"><X size={20} /></button>
              <h2 className="modal-title font-bold text-xl">
                 {isEditMode ? 'Modification du Dossier' : 'Création de Dossier Patient'}
              </h2>
            </div>
            
            <form onSubmit={handleSaveSubmit} className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 140px)' }}>
              
              <div className="mb-8">
                <h4 className="text-base font-bold text-main border-b border-color pb-2 mb-4">1. Identité et Localisation</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <label className="label">CIN *</label>
                    <input type="text" className="input" required value={formData.cin} onChange={e => setFormData({...formData, cin: e.target.value})} placeholder="ex: AB12345" />
                  </div>
                  <div>
                    <label className="label">Prénom *</label>
                    <input type="text" className="input" required value={formData.first_name} onChange={e => setFormData({...formData, first_name: e.target.value})} />
                  </div>
                  <div>
                    <label className="label">Nom *</label>
                    <input type="text" className="input" required value={formData.last_name} onChange={e => setFormData({...formData, last_name: e.target.value})} />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <label className="label">Date de naissance *</label>
                    <input type="date" className="input" required value={formData.date_of_birth} onChange={e => setFormData({...formData, date_of_birth: e.target.value})} />
                  </div>
                  <div>
                    <label className="label">Genre *</label>
                    <select className="input" required value={formData.gender} onChange={e => setFormData({...formData, gender: e.target.value})}>
                      <option value="M">Masculin</option>
                      <option value="F">Féminin</option>
                      <option value="O">Autre</option>
                    </select>
                  </div>
                  <div>
                    <label className="label">Ville *</label>
                    <select className="input" required value={formData.city} onChange={e => setFormData({...formData, city: e.target.value})}>
                      <option value="Casablanca">Casablanca</option>
                      <option value="Rabat">Rabat</option>
                      <option value="Fes">Fès</option>
                      <option value="Marrakech">Marrakech</option>
                      <option value="Tangier">Tanger</option>
                      <option value="Agadir">Agadir</option>
                      <option value="Meknes">Meknès</option>
                      <option value="Oujda">Oujda</option>
                      <option value="Other">Autre</option>
                    </select>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="label">Email</label>
                    <input type="email" className="input" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} placeholder="email@exemple.com" />
                  </div>
                  <div>
                    <label className="label">Téléphone</label>
                    <input type="tel" className="input" value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} placeholder="+212600000000" />
                  </div>
                  <div>
                    <label className="label">Contact d'urgence</label>
                    <input type="text" className="input" value={formData.emergency_contact} onChange={e => setFormData({...formData, emergency_contact: e.target.value})} placeholder="Nom et Tél de l'urgence" />
                  </div>
                </div>
              </div>

              <div className="mb-4">
                <h4 className="text-base font-bold text-danger border-b border-[#fecdd3] pb-2 mb-4 flex items-center gap-2">
                  <ShieldAlert size={18}/> 2. Profil Médical
                </h4>
                <div className="grid grid-cols-1 gap-4">
                  <div className="max-w-xs">
                    <label className="label">Groupe Sanguin</label>
                    <select className="input" value={formData.blood_group} onChange={e => setFormData({...formData, blood_group: e.target.value})}>
                      <option value="">-- Non connu --</option>
                      <option value="A+">A+</option><option value="A-">A-</option>
                      <option value="B+">B+</option><option value="B-">B-</option>
                      <option value="AB+">AB+</option><option value="AB-">AB-</option>
                      <option value="O+">O+</option><option value="O-">O-</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="label">Allergies</label>
                      <textarea className="input" rows="3" value={formData.allergies} onChange={e => setFormData({...formData, allergies: e.target.value})} placeholder="Pénicilline, arachides..."></textarea>
                    </div>
                    <div>
                      <label className="label">Antécédents médicaux / chirurgicaux</label>
                      <textarea className="input" rows="3" value={formData.medical_history} onChange={e => setFormData({...formData, medical_history: e.target.value})} placeholder="Diabète type 2, Appendicectomie (2015)..."></textarea>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 pb-4 px-6 border-t border-color sticky bottom-0 z-10" style={{ background: 'rgba(255, 255, 255, 0.85)', backdropFilter: 'blur(12px)', margin: '0 -1.5rem -1.5rem -1.5rem' }}>
                <button type="button" className="btn btn-outline" onClick={() => setIsModalOpen(false)}>Annuler</button>
                <button type="submit" className="btn btn-primary px-8">{isEditMode ? 'Enregistrer les modifications' : 'Créer le dossier'}</button>
              </div>
            </form>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
};

export default Patients;
