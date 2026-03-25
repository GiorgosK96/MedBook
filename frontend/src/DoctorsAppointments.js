import { useState, useEffect } from 'react';
import { useLanguage } from './LanguageContext';
import { useToast } from './components/ToastContext';
import { formatDate, formatTime } from './utils/formatDate';
import Spinner from './components/Spinner';
import ConfirmModal from './components/ConfirmModal';

const STATUS_STYLES = {
  pending: 'bg-amber-100 text-amber-700',
  confirmed: 'bg-green-100 text-green-700',
  declined: 'bg-red-100 text-red-700',
};

function DoctorsAppointments() {
  const { t, lang } = useLanguage();
  const showToast = useToast();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [confirmAction, setConfirmAction] = useState(null); // { id, type: 'cancel'|'accept'|'decline' }

  useEffect(() => {
    fetch('/doctorAppointments', { method: 'GET', headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
      .then(r => { if (r.ok) return r.json(); throw new Error(); })
      .then(data => setAppointments(data.appointments))
      .catch(() => showToast(t.errorOccurred, 'error'))
      .finally(() => setLoading(false));
  }, [t.errorOccurred, showToast]);

  const handleDelete = () => {
    const id = confirmAction.id;
    setConfirmAction(null);
    fetch(`/doctorAppointments/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
      .then(r => r.json().then(d => {
        if (r.ok) { showToast(d.message, 'success'); setAppointments(appointments.filter(a => a.id !== id)); }
        else showToast(d.message, 'error');
      }))
      .catch(() => showToast(t.errorOccurred, 'error'));
  };

  const handleStatusUpdate = (id, status) => {
    setConfirmAction(null);
    fetch(`/doctorAppointments/${id}/status`, {
      method: 'PATCH',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    })
      .then(r => r.json().then(d => {
        if (r.ok) { showToast(d.message, 'success'); setAppointments(appointments.map(a => a.id === id ? { ...a, status } : a)); }
        else showToast(d.error, 'error');
      }))
      .catch(() => showToast(t.errorOccurred, 'error'));
  };

  const statusLabel = (s) => s === 'confirmed' ? t.statusConfirmed : s === 'declined' ? t.statusDeclined : t.statusPending;

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-50 px-6 pb-10 pt-16 font-sans">
      <div className="max-w-xl mx-auto">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 text-center">{t.doctorAppointmentsTitle}</h2>

        {loading ? <Spinner /> : appointments.length === 0 ? (
          <div className="text-center py-16 bg-white border border-slate-200 rounded-xl shadow-sm mb-6">
            <p className="text-3xl mb-3 opacity-40">🩺</p>
            <p className="text-base font-semibold text-slate-800 mb-1">{t.noAppointmentsScheduled}</p>
            <p className="text-sm text-slate-500">{t.noAppointmentsScheduledDesc}</p>
          </div>
        ) : (
          <div className="space-y-3 mb-6">
            {appointments.map(a => (
              <div key={a.id} className={`bg-white border border-slate-200 rounded-xl p-5 shadow-sm ${a.status === 'declined' ? 'opacity-50' : ''}`}>
                <div className="grid grid-cols-[100px_1fr] gap-y-1.5 text-sm">
                  <span className="font-medium text-slate-500">{t.clientName}</span>
                  <span className="text-slate-800">{a.client.full_name}</span>
                  <span className="font-medium text-slate-500">{t.email}</span>
                  <span className="text-slate-800">{a.client.email}</span>
                  <span className="font-medium text-slate-500">{t.date}</span>
                  <span className="text-slate-800">{formatDate(a.date, lang)}</span>
                  <span className="font-medium text-slate-500">{t.time}</span>
                  <span className="text-slate-800">{formatTime(a.time_from)} – {formatTime(a.time_to)}</span>
                  <span className="font-medium text-slate-500">{t.status}</span>
                  <span><span className={`inline-block px-2 py-0.5 text-xs font-medium rounded-full ${STATUS_STYLES[a.status] || STATUS_STYLES.pending}`}>{statusLabel(a.status)}</span></span>
                  {a.comments && (<><span className="font-medium text-slate-500">{t.notes}</span><span className="text-slate-800">{a.comments}</span></>)}
                </div>
                {a.status !== 'declined' && (
                  <div className="flex gap-2 mt-4 pt-3 border-t border-slate-100">
                    {a.status === 'pending' && (
                      <>
                        <button onClick={() => setConfirmAction({ id: a.id, type: 'accept' })} className="px-3 py-1.5 text-xs font-medium text-green-600 border border-green-600 rounded-md hover:bg-green-50 transition-colors">{t.acceptAppointment}</button>
                        <button onClick={() => setConfirmAction({ id: a.id, type: 'decline' })} className="px-3 py-1.5 text-xs font-medium text-red-600 border border-red-600 rounded-md hover:bg-red-50 transition-colors">{t.declineAppointment}</button>
                      </>
                    )}
                    {a.status === 'confirmed' && (
                      <button onClick={() => setConfirmAction({ id: a.id, type: 'cancel' })} className="px-3 py-1.5 text-xs font-medium text-red-600 border border-red-600 rounded-md hover:bg-red-50 transition-colors">{t.cancelAppointment}</button>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {confirmAction && (
        <ConfirmModal
          message={
            confirmAction.type === 'accept' ? t.confirmAccept :
            confirmAction.type === 'decline' ? t.confirmDecline :
            t.confirmDelete
          }
          confirmLabel={
            confirmAction.type === 'accept' ? t.acceptAppointment :
            confirmAction.type === 'decline' ? t.declineAppointment :
            undefined
          }
          variant={confirmAction.type === 'accept' ? 'success' : 'danger'}
          onConfirm={() => {
            if (confirmAction.type === 'accept') handleStatusUpdate(confirmAction.id, 'confirmed');
            else if (confirmAction.type === 'decline') handleStatusUpdate(confirmAction.id, 'declined');
            else handleDelete();
          }}
          onCancel={() => setConfirmAction(null)}
        />
      )}
    </div>
  );
}

export default DoctorsAppointments;
