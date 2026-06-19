import React, { useState, useEffect, useMemo } from 'react';
import { createPortal } from 'react-dom';
import api from '../services/api';
import useToastStore from '../store/useToastStore';
import { Calendar as CalendarIcon, Clock, User, FileText, X, Edit, Trash2, CheckCircle, Slash, Search, Plus } from 'lucide-react';
import Spinner from '../components/Spinner';

const Appointments = () => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [selectedAppt, setSelectedAppt] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const [currentPage, setCurrentPage] = useState(1);
  const ITEMS_PER_PAGE = 8;

  const [patientsList, setPatientsList] = useState([]);
  const [doctorsList, setDoctorsList] = useState([]);
  
  const { addToast } = useToastStore();
  
  const initialForm = {
    patient: '', doctor: '', date: '', time: '', duration: 30, reason: '', status: 'PLANNED'
  };
  const [formData, setFormData] = useState(initialForm);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [resApps, resPats, resDocs] = await Promise.all([
        api.get('/appointments/'),
        api.get('/patients/'),
        api.get('/auth/users/')
      ]);
      setAppointments(resApps.data);
      setPatientsList(resPats.data);
      setDoctorsList(resDocs.data.filter(u => u.role === 'DOCTOR') || []);
    } catch (err) {
      console.error(err);
      if(appointments.length === 0) {
          api.get('/appointments/').then(r => setAppointments(r.data)).catch(e => console.log(e));
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const openNewApptModal = () => {
    setFormData(initialForm);
    setIsEditMode(false);
    setIsModalOpen(true);
  };

  const handleEditClick = (a) => {
    setSelectedAppt(a);
    setFormData({
      patient: a.patient,
      doctor: a.doctor,
      date: a.date,
      time: a.time,
      duration: a.duration,
      reason: a.reason,
      status: a.status
    });
    setIsEditMode(true);
    setIsModalOpen(true);
  };

  const handleStatusChange = async (id, newStatus) => {
    try {
      await api.patch(`/appointments/${id}/`, { status: newStatus });
      addToast('Statut mis à jour', `Le rendez-vous est maintenant ${newStatus}`, 'success');
      fetchData();
    } catch (err) {
      console.error(err);
      addToast('Erreur', 'Impossible de changer le statut', 'error');
    }
  };

  const handleDelete = async (id) => {
    if(window.confirm("Êtes-vous sûr de vouloir supprimer définitivement ce rendez-vous ?")) {
      try {
        await api.delete(`/appointments/${id}/`);
        addToast('Supprimé', 'Rendez-vous annulé et supprimé.', 'success');
        fetchData();
      } catch (err) {
        console.error(err);
        addToast('Erreur', 'Erreur lors de la suppression.', 'error');
      }
    }
  };

  const handleSaveSubmit = async (e) => {
    e.preventDefault();

    // Validation to prevent scheduling in the past
    if (formData.date && formData.time) {
      const selectedDateTime = new Date(`${formData.date}T${formData.time}`);
      if (selectedDateTime < new Date()) {
        addToast('Date Invalide', 'Impossible de planifier un rendez-vous dans le passé.', 'warning');
        return;
      }
    }

    try {
      if (isEditMode && selectedAppt) {
        await api.put(`/appointments/${selectedAppt.id}/`, formData);
        addToast('Succès', 'Rendez-vous mis à jour avec succès.', 'success');
      } else {
        await api.post('/appointments/', formData);
        addToast('Succès', 'Nouveau rendez-vous créé.', 'success');
      }
      setIsModalOpen(false);
      fetchData();
    } catch (err) {
      console.error(err);
      if(err.response?.data?.non_field_errors) {
        addToast('Conflit d\'agenda', err.response.data.non_field_errors[0], 'warning');
      } else {
        addToast('Erreur', "Erreur lors de l'enregistrement", 'error');
      }
    }
  };

  const getStatusBadge = (status) => {
    switch(status) {
      case 'PLANNED': return <span className="badge badge-warning">Planifié</span>;
      case 'CONFIRMED': return <span className="badge badge-primary">Confirmé</span>;
      case 'IN_PROGRESS': return <span className="badge bg-yellow-100 text-yellow-800">En cours</span>;
      case 'COMPLETED': return <span className="badge badge-success">Terminé</span>;
      case 'CANCELLED': return <span className="badge bg-slate-200 text-slate-600">Annulé</span>;
      default: return <span className="badge">{status}</span>;
    }
  };

  const filteredAppointments = useMemo(() => {
    if (!searchQuery) return appointments;
    const lowerQ = searchQuery.toLowerCase();
    return appointments.filter(a => {
      const pName = a.patient_details ? `${a.patient_details.first_name} ${a.patient_details.last_name}`.toLowerCase() : '';
      const dName = a.doctor_details ? `dr. ${a.doctor_details.last_name}`.toLowerCase() : '';
      const reason = (a.reason || '').toLowerCase();
      const status = (a.status || '').toLowerCase();
      const date = (a.date || '').toLowerCase();
      return pName.includes(lowerQ) || dName.includes(lowerQ) || reason.includes(lowerQ) || status.includes(lowerQ) || date.includes(lowerQ);
    });
  }, [appointments, searchQuery]);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, appointments]);

  return (
    <div className="animate-fade-in">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-main m-0 tracking-tight">Agenda</h1>
          <p className="text-muted mt-1">Gérez le planning des consultations.</p>
        </div>
        <button className="btn btn-primary" onClick={openNewApptModal}>
          <Plus size={18} /> Nouveau Rendez-vous
        </button>
      </div>

      <div className="card mb-6 p-4">
        <form onSubmit={e => e.preventDefault()} className="flex gap-4 w-full">
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search size={18} className="text-light" />
            </div>
            <input 
              type="text" 
              className="input pl-10 w-full" 
              placeholder="Rechercher par patient, docteur, date ou statut..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </form>
      </div>

      <div className="card p-0 overflow-hidden shadow-sm">
        {loading ? (
          <Spinner size={40} />
        ) : appointments.length === 0 ? (
          <div className="p-12 text-center text-muted">
             <CalendarIcon size={64} className="mx-auto mb-4 opacity-20 text-primary" />
             <p className="text-lg">Aucun rendez-vous planifié.</p>
          </div>
        ) : (
          <div className="table-wrapper border-0">
            <table className="table">
              <thead>
                <tr>
                  <th>Date & Heure</th>
                  <th>Patient</th>
                  <th>Motif</th>
                  <th>Docteur & Statut</th>
                  <th className="text-right">Actions Rapides</th>
                </tr>
              </thead>
              <tbody>
                {filteredAppointments.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE).map(a => (
                  <tr key={a.id} className={a.status === 'CANCELLED' ? 'opacity-50 grayscale' : ''}>
                    <td>
                      <div className="font-semibold text-main mb-1 flex items-center gap-2">
                        <CalendarIcon size={14} className="text-primary"/> {a.date}
                      </div>
                      <div className="text-sm text-light flex items-center gap-2">
                        <Clock size={14}/> {a.time.substring(0,5)} <span className="opacity-70">({a.duration}m)</span>
                      </div>
                    </td>
                    <td>
                      <div className="font-medium text-main flex items-center gap-2">
                        <User size={14} className="text-muted"/> 
                        {a.patient_details ? `${a.patient_details.first_name} ${a.patient_details.last_name}` : `Patient #${a.patient}`}
                      </div>
                    </td>
                    <td>
                      <div className="text-sm text-main flex items-start gap-2 max-w-xs">
                        <FileText size={14} className="text-muted mt-1 shrink-0"/> 
                        <span className="truncate" title={a.reason}>{a.reason}</span>
                      </div>
                    </td>
                    <td>
                       <div className="text-sm font-medium text-main mb-2">
                         {a.doctor_details ? `Dr. ${a.doctor_details.last_name}` : `Doc #${a.doctor}`}
                       </div>
                       {getStatusBadge(a.status)}
                    </td>
                    <td>
                      <div className="flex justify-end gap-1 flex-wrap">
                        {a.status === 'PLANNED' && (
                          <button className="btn btn-outline text-success border-transparent hover:bg-success-light" title="Confirmer" onClick={() => handleStatusChange(a.id, 'CONFIRMED')}>
                            <CheckCircle size={16} />
                          </button>
                        )}
                        {(a.status === 'PLANNED' || a.status === 'CONFIRMED') && (
                          <button className="btn btn-outline text-muted border-transparent hover:bg-hover" title="Annuler" onClick={() => handleStatusChange(a.id, 'CANCELLED')}>
                            <Slash size={16} />
                          </button>
                        )}
                        
                        <div className="w-px h-6 bg-border-color mx-1 my-auto"></div>
                        
                        <button className="btn btn-outline-primary btn-icon border-transparent" onClick={() => handleEditClick(a)} title="Modifier">
                          <Edit size={16}/>
                        </button>
                        <button className="btn btn-outline-danger btn-icon border-transparent" onClick={() => handleDelete(a.id)} title="Supprimer de la BDD">
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {filteredAppointments.length > ITEMS_PER_PAGE && (
          <div className="flex justify-between items-center p-4 bg-hover border-t border-color">
            <span className="text-sm text-light font-medium">
              Affiche {(currentPage - 1) * ITEMS_PER_PAGE + 1} à {Math.min(currentPage * ITEMS_PER_PAGE, filteredAppointments.length)} sur {filteredAppointments.length} rdv
            </span>
            <div className="flex gap-2">
              <button 
                className="btn btn-outline py-1 px-3 text-sm" 
                disabled={currentPage === 1} 
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              >
                Précédent
              </button>
              {[...Array(Math.ceil(filteredAppointments.length / ITEMS_PER_PAGE))].map((_, i) => (
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
                disabled={currentPage === Math.ceil(filteredAppointments.length / ITEMS_PER_PAGE) || Math.ceil(filteredAppointments.length / ITEMS_PER_PAGE) === 0} 
                onClick={() => setCurrentPage(prev => prev + 1)}
              >
                Suivant
              </button>
            </div>
          </div>
        )}
      </div>

      {isModalOpen && createPortal(
        <div className="modal-overlay">
          <div className="modal-content card max-w-2xl p-0">
            <div className="modal-header p-6 pb-4 bg-primary-light border-b border-color rounded-t-lg">
              <button onClick={() => setIsModalOpen(false)} className="modal-close"><X size={20} /></button>
              <h2 className="modal-title text-primary font-bold text-xl">
                {isEditMode ? 'Modifier le Rendez-vous' : 'Planifier un Rendez-vous'}
              </h2>
            </div>
            
            <form onSubmit={handleSaveSubmit} className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(85vh - 100px)' }}>
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="label">Patient *</label>
                  <select className="input" required value={formData.patient} onChange={e => setFormData({...formData, patient: e.target.value})}>
                    <option value="">-- Sélectionner --</option>
                    {patientsList.map(p => <option key={p.id} value={p.id}>{p.cin ? `[${p.cin}] ` : ''}{p.first_name} {p.last_name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="label">Docteur *</label>
                  <select className="input" required value={formData.doctor} onChange={e => setFormData({...formData, doctor: e.target.value})}>
                    <option value="">-- Sélectionner --</option>
                    {doctorsList.map(d => <option key={d.id} value={d.id}>Dr. {d.first_name} {d.last_name}</option>)}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="label">Date *</label>
                  <input type="date" className="input" required min={new Date().toISOString().split('T')[0]} value={formData.date} onChange={e => setFormData({...formData, date: e.target.value})} />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="label">Heure *</label>
                    <input type="time" className="input" required value={formData.time} onChange={e => setFormData({...formData, time: e.target.value})} />
                  </div>
                  <div>
                    <label className="label">Durée (m)</label>
                    <input type="number" className="input" required value={formData.duration} onChange={e => setFormData({...formData, duration: e.target.value})} min="5" step="5" />
                  </div>
                </div>
              </div>

              <div className="mb-4">
                <label className="label">Motif de la consultation *</label>
                <input type="text" className="input" required placeholder="Ex: Consultation de suivi..." value={formData.reason} onChange={e => setFormData({...formData, reason: e.target.value})} />
              </div>

              {isEditMode && (
                <div className="mb-4">
                  <label className="label">Statut</label>
                  <select className="input" value={formData.status} onChange={e => setFormData({...formData, status: e.target.value})}>
                    <option value="PLANNED">Planifié</option>
                    <option value="CONFIRMED">Confirmé</option>
                    <option value="IN_PROGRESS">En cours</option>
                    <option value="COMPLETED">Terminé</option>
                    <option value="CANCELLED">Annulé</option>
                  </select>
                </div>
              )}

              <div className="flex justify-end gap-3 mt-8">
                <button type="button" className="btn btn-outline" onClick={() => setIsModalOpen(false)}>Annuler</button>
                <button type="submit" className="btn btn-primary px-8">{isEditMode ? 'Enregistrer' : 'Confirmer'}</button>
              </div>
            </form>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
};

export default Appointments;
