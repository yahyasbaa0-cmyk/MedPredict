import React from 'react';
import useToastStore from '../store/useToastStore';
import { CheckCircle, XCircle, Info, AlertTriangle, X } from 'lucide-react';

const ToastProvider = () => {
  const { toasts, removeToast } = useToastStore();

  if (toasts.length === 0) return null;

  return (
    <div className="toast-container">
      {toasts.map((toast) => {
        let Icon = Info;
        let color = 'var(--primary)';
        
        switch (toast.type) {
          case 'success': Icon = CheckCircle; color = 'var(--success)'; break;
          case 'error': Icon = XCircle; color = 'var(--danger)'; break;
          case 'warning': Icon = AlertTriangle; color = 'var(--warning)'; break;
          default: break;
        }

        return (
          <div key={toast.id} className={`toast toast-${toast.type}`}>
            <div style={{ color, marginTop: '2px' }}><Icon size={20} /></div>
            <div className="toast-content">
              {toast.title && <div className="toast-title">{toast.title}</div>}
              {toast.message && <div className="toast-message">{toast.message}</div>}
            </div>
            <button onClick={() => removeToast(toast.id)} className="toast-close">
              <X size={16} />
            </button>
          </div>
        );
      })}
    </div>
  );
};

export default ToastProvider;
