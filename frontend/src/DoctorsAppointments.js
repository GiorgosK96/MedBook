import { useState, useEffect } from 'react';
import { useLanguage } from './LanguageContext';
import { useToast } from './components/ToastContext';
import { formatDate, formatTime } from './utils/formatDate';
import { apiFetch } from './utils/apiFetch';
import Spinner from './components/Spinner';
import ConfirmModal from './components/ConfirmModal';
import StatusBadge from './components/StatusBadge';

function DoctorsAppointments() {
  const { t, lang } = useLanguage();
  const showToast = useToast();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [confirmAction, setConfirmAction] = useState(null);  // { id, status }

  useEffect(() => {
    apiFetch('/doctorAppointments')
      .then(r => r && r.json())
      .then(data => data && setAppointments(data.appointments))
      .catch(() => showToast(t.errorOccurred, 'error'))
      .finally(() => setLoading(false));
  }, [t.errorOccurred, showToast]);

  const handleStatusUpdate = () => {
    const { id, status } = confirmAction;
    setConfirmAction(null);
    apiFetch(`/doctorAppointments/${id}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    })
      .then(r => r && r.json().then(d => {
        if (!r.ok) { showToast(d.error, 'error'); return; }
        showToast(d.message, 'success');
        setAppointments(prev => prev.map(a => a.id === id ? { ...a, status } : a));
      }))
      .catch(() => showToast(t.errorOccurred, 'error'));
  };

  // [confirmation message, button label] for each status a doctor can set
  const confirmText = {
    confirmed: [t.confirmAccept, t.acceptAppointment],
    declined: [t.confirmDecline, t.declineAppointment],
    cancelled: [t.confirmCancel, t.cancelAppointment],
  };

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
              <div key={a.id} className={`bg-white border border-slate-200 rounded-xl p-5 shadow-sm ${a.status === 'declined' || a.status === 'cancelled' ? 'opacity-50' : ''}`}>
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
                  <span><StatusBadge status={a.status} /></span>
                  {a.comments && (<><span className="font-medium text-slate-500">{t.notes}</span><span className="text-slate-800">{a.comments}</span></>)}
                </div>
                {(a.status === 'pending' || a.status === 'confirmed') && (
                  <div className="flex gap-2 mt-4 pt-3 border-t border-slate-100">
                    {a.status === 'pending' && (
                      <>
                        <button onClick={() => setConfirmAction({ id: a.id, status: 'confirmed' })} className="px-3 py-1.5 text-xs font-medium text-green-600 border border-green-600 rounded-md hover:bg-green-50 transition-colors">{t.acceptAppointment}</button>
                        <button onClick={() => setConfirmAction({ id: a.id, status: 'declined' })} className="px-3 py-1.5 text-xs font-medium text-red-600 border border-red-600 rounded-md hover:bg-red-50 transition-colors">{t.declineAppointment}</button>
                      </>
                    )}
                    {a.status === 'confirmed' && (
                      <button onClick={() => setConfirmAction({ id: a.id, status: 'cancelled' })} className="px-3 py-1.5 text-xs font-medium text-red-600 border border-red-600 rounded-md hover:bg-red-50 transition-colors">{t.cancelAppointment}</button>
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
          message={confirmText[confirmAction.status][0]}
          confirmLabel={confirmText[confirmAction.status][1]}
          variant={confirmAction.status === 'confirmed' ? 'success' : 'danger'}
          onConfirm={handleStatusUpdate}
          onCancel={() => setConfirmAction(null)}
        />
      )}
    </div>
  );
}

export default DoctorsAppointments;
