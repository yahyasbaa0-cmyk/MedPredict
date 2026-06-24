import React, { useState, useEffect, useMemo } from 'react';
import { createPortal } from 'react-dom';
import api from '../services/api';
import useToastStore from '../store/useToastStore';
import { Users, Plus, Search, Edit, Trash2, Key, X, Shield, Lock, Phone, Mail, UserCheck, User } from 'lucide-react';
import Spinner from '../components/Spinner';
import useAuthStore from '../store/useAuthStore';

const AdminPanel = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('ALL');
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  
  const { addToast } = useToastStore();
  const currentUser = useAuthStore(state => state.user);

  const initialForm = {
    username: '',
    first_name: '',
    last_name: '',
    email: '',
    role: 'SECRETARY',
    phone: '',
    password: ''
  };
  
  const [formData, setFormData] = useState(initialForm);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await api.get('/auth/users/');
      setUsers(res.data);
    } catch (err) {
      console.error(err);
      addToast('Erreur', 'Impossible de charger les comptes utilisateurs.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const openNewUserModal = () => {
    setFormData(initialForm);
    setIsEditMode(false);
    setIsModalOpen(true);
  };

  const handleEditClick = (u) => {
    setSelectedUser(u);
    setFormData({
      username: u.username || '',
      first_name: u.first_name || '',
      last_name: u.last_name || '',
      email: u.email || '',
      role: u.role || 'SECRETARY',
      phone: u.phone || '',
      password: '' // Hide password for edits
    });
    setIsEditMode(true);
    setIsModalOpen(true);
  };

  const handleSaveSubmit = async (e) => {
    e.preventDefault();
    try {
      // Create payload. Remove password on edit if empty
      const payload = { ...formData };
      if (isEditMode) {
        delete payload.username; // Cannot change username on edit in typical setups
        if (!payload.password) {
          delete payload.password;
        }
      }

      if (isEditMode && selectedUser) {
        await api.put(`/auth/users/${selectedUser.id}/`, payload);
        addToast('Succès', 'Utilisateur mis à jour avec succès.', 'success');
      } else {
        await api.post('/auth/users/', payload);
        addToast('Succès', 'Nouvel utilisateur créé avec succès.', 'success');
      }
      setIsModalOpen(false);
      fetchUsers();
    } catch (err) {
      console.error(err);
      const detail = err.response?.data ? Object.values(err.response.data).flat().join(' ') : "Erreur lors de l'enregistrement.";
      addToast('Erreur', detail, 'error');
    }
  };

  const handleDeleteUser = async (u) => {
    if (u.id === currentUser?.id) {
      addToast('Action interdite', 'Vous ne pouvez pas supprimer votre propre compte.', 'warning');
      return;
    }
    
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer définitivement le compte de ${u.first_name} ${u.last_name} (${u.username}) ?`)) {
      try {
        await api.delete(`/auth/users/${u.id}/`);
        addToast('Supprimé', 'Compte utilisateur supprimé avec succès.', 'success');
        fetchUsers();
      } catch (err) {
        console.error(err);
        addToast('Erreur', 'Impossible de supprimer cet utilisateur.', 'error');
      }
    }
  };

  const handleResetPassword = async (u) => {
    const customPassword = window.prompt(
      `Entrez le nouveau mot de passe pour ${u.first_name} ${u.last_name} :\n(Laissez vide pour utiliser le mot de passe par défaut : ${u.username}2025)`
    );

    if (customPassword !== null) {
      try {
        const payload = customPassword ? { password: customPassword } : {};
        const res = await api.post(`/auth/users/${u.id}/reset-password/`, payload);
        const resolvedPass = res.data.new_password || customPassword || `${u.username}2025`;
        addToast('Mot de passe réinitialisé', `Nouveau mot de passe : ${resolvedPass}`, 'success');
      } catch (err) {
        console.error(err);
        addToast('Erreur', 'Impossible de réinitialiser le mot de passe.', 'error');
      }
    }
  };

  const filteredUsers = useMemo(() => {
    return users.filter(u => {
      // Filter by role
      if (roleFilter !== 'ALL' && u.role !== roleFilter) return false;
      
      // Filter by search query
      if (!searchQuery) return true;
      const lowerQ = searchQuery.toLowerCase();
      const fullName = `${u.first_name} ${u.last_name}`.toLowerCase();
      return (
        fullName.includes(lowerQ) ||
        (u.username || '').toLowerCase().includes(lowerQ) ||
        (u.email || '').toLowerCase().includes(lowerQ) ||
        (u.phone || '').toLowerCase().includes(lowerQ)
      );
    });
  }, [users, searchQuery, roleFilter]);

  // Statistics counters
  const stats = useMemo(() => {
    const result = { total: users.length, admins: 0, doctors: 0, secretaries: 0, patients: 0 };
    users.forEach(u => {
      if (u.role === 'ADMIN') result.admins++;
      else if (u.role === 'DOCTOR') result.doctors++;
      else if (u.role === 'SECRETARY') result.secretaries++;
      else if (u.role === 'PATIENT') result.patients++;
    });
    return result;
  }, [users]);

  const getRoleBadge = (role) => {
    switch (role) {
      case 'ADMIN':
        return <span className="badge badge-danger"><Shield size={12} /> Administrateur</span>;
      case 'DOCTOR':
        return <span className="badge badge-primary"><UserCheck size={12} /> Médecin</span>;
      case 'SECRETARY':
        return <span className="badge badge-success"><Users size={12} /> Secrétaire</span>;
      case 'PATIENT':
        return <span className="badge badge-warning"><User size={12} /> Patient</span>;
      default:
        return <span className="badge">{role}</span>;
    }
  };

  return (
    <div className="animate-fade-in">
      {/* Title Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-main m-0 tracking-tight">Panneau d'administration</h1>
          <p className="text-muted mt-1">Gérez les comptes des médecins, secrétaires et administrateurs du cabinet.</p>
        </div>
        <button onClick={openNewUserModal} className="btn btn-primary">
          <Plus size={18} /> Ajouter un utilisateur
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 mb-8" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
        <div className="card p-6 flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-light uppercase tracking-wider block">Total Personnel</span>
            <span className="text-3xl font-extrabold text-main mt-2 block">{stats.total}</span>
          </div>
          <div className="p-3 bg-primary-light rounded-lg text-primary">
            <Users size={24} />
          </div>
        </div>

        <div className="card p-6 flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-light uppercase tracking-wider block">Médecins</span>
            <span className="text-3xl font-extrabold text-main mt-2 block">{stats.doctors}</span>
          </div>
          <div className="p-3 bg-success-light rounded-lg text-success">
            <UserCheck size={24} />
          </div>
        </div>

        <div className="card p-6 flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-light uppercase tracking-wider block">Secrétaires</span>
            <span className="text-3xl font-extrabold text-main mt-2 block">{stats.secretaries}</span>
          </div>
          <div className="p-3 bg-warning-light rounded-lg text-warning">
            <Users size={24} />
          </div>
        </div>

        <div className="card p-6 flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-light uppercase tracking-wider block">Patients</span>
            <span className="text-3xl font-extrabold text-main mt-2 block">{stats.patients}</span>
          </div>
          <div className="p-3 bg-warning-light rounded-lg text-warning" style={{ filter: 'hue-rotate(240deg)' }}>
            <User size={24} />
          </div>
        </div>

        <div className="card p-6 flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-light uppercase tracking-wider block">Administrateurs</span>
            <span className="text-3xl font-extrabold text-main mt-2 block">{stats.admins}</span>
          </div>
          <div className="p-3 bg-danger-light rounded-lg text-danger">
            <Shield size={24} />
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="card mb-6 p-4 flex gap-4 items-center">
        <div className="relative flex-1">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search size={18} className="text-light" />
          </div>
          <input
            type="text"
            className="input pl-10 w-full"
            placeholder="Rechercher par nom, nom d'utilisateur, email ou téléphone..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={() => setRoleFilter('ALL')}
            className={`btn py-2 px-4 text-sm ${roleFilter === 'ALL' ? 'btn-secondary' : 'btn-outline'}`}
          >
            Tous
          </button>
          <button
            onClick={() => setRoleFilter('DOCTOR')}
            className={`btn py-2 px-4 text-sm ${roleFilter === 'DOCTOR' ? 'btn-secondary' : 'btn-outline'}`}
          >
            Médecins
          </button>
          <button
            onClick={() => setRoleFilter('SECRETARY')}
            className={`btn py-2 px-4 text-sm ${roleFilter === 'SECRETARY' ? 'btn-secondary' : 'btn-outline'}`}
          >
            Secrétaires
          </button>
          <button
            onClick={() => setRoleFilter('PATIENT')}
            className={`btn py-2 px-4 text-sm ${roleFilter === 'PATIENT' ? 'btn-secondary' : 'btn-outline'}`}
          >
            Patients
          </button>
          <button
            onClick={() => setRoleFilter('ADMIN')}
            className={`btn py-2 px-4 text-sm ${roleFilter === 'ADMIN' ? 'btn-secondary' : 'btn-outline'}`}
          >
            Admins
          </button>
        </div>
      </div>

      {/* Users Table */}
      <div className="card p-0 overflow-hidden shadow-sm">
        {loading ? (
          <div className="p-12 text-center flex justify-center"><Spinner size={40} /></div>
        ) : filteredUsers.length === 0 ? (
          <div className="p-12 text-center text-muted">
            <Users size={64} className="mx-auto mb-4 opacity-20 text-primary" />
            <p className="text-lg font-medium">Aucun utilisateur trouvé.</p>
          </div>
        ) : (
          <div className="table-wrapper border-0">
            <table className="table">
              <thead>
                <tr>
                  <th>Nom Complet / Utilisateur</th>
                  <th>Rôle</th>
                  <th>Contact</th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map(u => (
                  <tr key={u.id}>
                    <td>
                      <div className="font-semibold text-main text-base">{u.first_name} {u.last_name}</div>
                      <div className="text-sm text-light mt-1">@{u.username}</div>
                    </td>
                    <td>
                      {getRoleBadge(u.role)}
                    </td>
                    <td>
                      <div className="text-sm text-main font-medium flex items-center gap-1.5">
                        <Mail size={13} className="text-light" />
                        <span>{u.email || '-'}</span>
                      </div>
                      <div className="text-sm text-light mt-1 flex items-center gap-1.5">
                        <Phone size={13} className="text-light" />
                        <span>{u.phone || '-'}</span>
                      </div>
                    </td>
                    <td>
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => handleResetPassword(u)}
                          className="btn btn-outline flex items-center gap-1 text-warning border-transparent hover:bg-warning-light"
                          title="Réinitialiser le mot de passe"
                        >
                          <Key size={15} />
                          <span className="hidden sm:inline">MDP</span>
                        </button>
                        <button
                          onClick={() => handleEditClick(u)}
                          className="btn btn-outline-primary btn-icon border-transparent"
                          title="Modifier"
                        >
                          <Edit size={16} />
                        </button>
                        <button
                          onClick={() => handleDeleteUser(u)}
                          className="btn btn-outline-danger btn-icon border-transparent"
                          disabled={u.id === currentUser?.id}
                          title="Supprimer"
                        >
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
      </div>

      {/* Create / Edit User Modal */}
      {isModalOpen && createPortal(
        <div className="modal-overlay">
          <div className="modal-content card max-w-2xl p-0">
            <div className="modal-header p-6 pb-4 bg-primary-light border-b border-color rounded-t-lg">
              <button onClick={() => setIsModalOpen(false)} className="modal-close"><X size={20} /></button>
              <h2 className="modal-title text-primary font-bold text-xl">
                {isEditMode ? "Modifier le compte utilisateur" : "Créer un compte personnel"}
              </h2>
            </div>

            <form onSubmit={handleSaveSubmit} className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(85vh - 100px)' }}>
              
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="label">Prénom *</label>
                  <input
                    type="text"
                    className="input"
                    required
                    value={formData.first_name}
                    onChange={e => setFormData({ ...formData, first_name: e.target.value })}
                  />
                </div>
                <div>
                  <label className="label">Nom de famille *</label>
                  <input
                    type="text"
                    className="input"
                    required
                    value={formData.last_name}
                    onChange={e => setFormData({ ...formData, last_name: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="label">Nom d'utilisateur (Login) *</label>
                  <input
                    type="text"
                    className="input"
                    required
                    disabled={isEditMode}
                    value={formData.username}
                    onChange={e => setFormData({ ...formData, username: e.target.value })}
                    placeholder="ex: dr_alami"
                  />
                </div>
                <div>
                  <label className="label">Rôle *</label>
                  <select
                    className="input"
                    required
                    value={formData.role}
                    onChange={e => setFormData({ ...formData, role: e.target.value })}
                  >
                    <option value="DOCTOR">Médecin (DOCTOR)</option>
                    <option value="SECRETARY">Secrétaire (SECRETARY)</option>
                    <option value="ADMIN">Administrateur (ADMIN)</option>
                    <option value="PATIENT">Patient (PATIENT)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="label">Adresse Email *</label>
                  <input
                    type="email"
                    className="input"
                    required
                    value={formData.email}
                    onChange={e => setFormData({ ...formData, email: e.target.value })}
                    placeholder="ex: nom@medpredict.ma"
                  />
                </div>
                <div>
                  <label className="label">N° Téléphone</label>
                  <input
                    type="tel"
                    className="input"
                    value={formData.phone}
                    onChange={e => setFormData({ ...formData, phone: e.target.value })}
                    placeholder="ex: +212600123456"
                  />
                </div>
              </div>

              {/* Password field - mandatory on create, optional/hidden on edit (using Reset button instead) */}
              {!isEditMode ? (
                <div className="mb-4">
                  <label className="label">Mot de passe initial *</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Lock size={16} className="text-light" />
                    </div>
                    <input
                      type="password"
                      className="input pl-10"
                      required
                      value={formData.password}
                      onChange={e => setFormData({ ...formData, password: e.target.value })}
                      placeholder="Définir un mot de passe sécurisé..."
                    />
                  </div>
                </div>
              ) : (
                <div className="mb-4 bg-primary-light p-4 rounded-lg border border-color flex items-start gap-3">
                  <Key className="text-primary mt-0.5 shrink-0" size={18} />
                  <div>
                    <span className="text-sm font-semibold text-main block">Changement de mot de passe</span>
                    <span className="text-xs text-muted mt-1 block">
                      Pour modifier le mot de passe de cet utilisateur, utilisez le bouton <strong>"MDP"</strong> (Clé) directement dans la liste des utilisateurs.
                    </span>
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-3 mt-8">
                <button type="button" className="btn btn-outline" onClick={() => setIsModalOpen(false)}>
                  Annuler
                </button>
                <button type="submit" className="btn btn-primary px-8">
                  {isEditMode ? "Enregistrer les modifications" : "Créer le compte"}
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

export default AdminPanel;
