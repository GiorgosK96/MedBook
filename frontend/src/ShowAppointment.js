import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from './LanguageContext';
import { useToast } from './components/ToastContext';
import { formatDate, formatTime, todayLocal } from './utils/formatDate';
import { apiFetch } from './utils/apiFetch';
import Spinner from './components/Spinner';
import ConfirmModal from './components/ConfirmModal';
import StatusBadge from './components/StatusBadge';

function AppointmentCard({ appointment: a, isPast, onCancel }) {
  const { t, lang } = useLanguage();
  const navigate = useNavigate();
  const canEdit = !isPast && a.status === 'pending';
  const canCancel = !isPast && (a.status === 'pending' || a.status === 'confirmed');

  return (
    <div className={`bg-white border border-slate-200 rounded-xl p-5 shadow-sm ${isPast ? 'opacity-50' : ''}`}>
      <div className="grid grid-cols-[80px_1fr] gap-y-1.5 text-sm">
        <span className="font-medium text-slate-500">{t.date}</span>
        <span className="text-slate-800">{formatDate(a.date, lang)}</span>
        <span className="font-medium text-slate-500">{t.time}</span>
        <span className="text-slate-800">{formatTime(a.time_from)} – {formatTime(a.time_to)}</span>
        <span className="font-medium text-slate-500">{t.doctor}</span>
        <span className="text-slate-800">{a.doctor.full_name} ({a.doctor.specialization})</span>
        <span className="font-medium text-slate-500">{t.status}</span>
        <span><StatusBadge status={a.status} /></span>
        {a.comments && (<><span className="font-medium text-slate-500">{t.notes}</span><span className="text-slate-800">{a.comments}</span></>)}
      </div>
      {(canEdit || canCancel) && (
        <div className="flex gap-2 mt-4 pt-3 border-t border-slate-100">
          {canEdit && <button onClick={() => navigate(`/UpdateAppointment/${a.id}`)} className="px-3 py-1.5 text-xs font-medium text-blue-600 border border-blue-600 rounded-md hover:bg-blue-50 transition-colors">{t.edit}</button>}
          {canCancel && <button onClick={() => onCancel(a.id)} className="px-3 py-1.5 text-xs font-medium text-red-600 border border-red-600 rounded-md hover:bg-red-50 transition-colors">{t.cancelAppointment}</button>}
        </div>
      )}
    </div>
  );
}

function ShowAppointment() {
  const { t } = useLanguage();
  const showToast = useToast();
  const navigate = useNavigate();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cancelId, setCancelId] = useState(null);

  useEffect(() => {
    apiFetch('/ShowAppointment')
      .then(r => r && r.json())
      .then(data => data && setAppointments(data.appointments))
      .catch(() => showToast(t.errorOccurred, 'error'))
      .finally(() => setLoading(false));
  }, [t.errorOccurred, showToast]);

  const handleCancel = () => {
    const id = cancelId;
    setCancelId(null);
    apiFetch(`/ShowAppointment/${id}`, { method: 'DELETE' })
      .then(r => r && r.json().then(d => {
        if (!r.ok) { showToast(d.error, 'error'); return; }
        showToast(d.message, 'success');
        setAppointments(prev => prev.map(a => a.id === id ? { ...a, status: 'cancelled' } : a));
      }))
      .catch(() => showToast(t.errorOccurred, 'error'));
  };

  const today = todayLocal();
  const upcoming = appointments.filter(a => a.date >= today);
  const past = appointments.filter(a => a.date < today);

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-50 px-6 pb-10 pt-20 font-sans">
      <div className="max-w-lg mx-auto">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 text-center">{t.yourAppointments}</h2>

        {loading ? <Spinner /> : appointments.length === 0 ? (
          <div className="text-center py-16 bg-white border border-slate-200 rounded-xl shadow-sm mb-6">
            <p className="text-3xl mb-3 opacity-40">📅</p>
            <p className="text-base font-semibold text-slate-800 mb-1">{t.noAppointmentsYet}</p>
            <p className="text-sm text-slate-500 mb-6">{t.noAppointmentsDesc}</p>
            <button onClick={() => navigate('/AddAppointment')} className="px-5 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
              {t.newAppointment}
            </button>
          </div>
        ) : (
          <div className="space-y-3 mb-6">
            {upcoming.map(a => <AppointmentCard key={a.id} appointment={a} onCancel={setCancelId} />)}
            {past.length > 0 && upcoming.length > 0 && (
              <p className="text-xs text-slate-400 text-center pt-2 pb-1">— {t.past} —</p>
            )}
            {past.map(a => <AppointmentCard key={a.id} appointment={a} isPast onCancel={setCancelId} />)}
          </div>
        )}
      </div>

      {cancelId && <ConfirmModal message={t.confirmCancel} confirmLabel={t.cancelAppointment} onConfirm={handleCancel} onCancel={() => setCancelId(null)} />}
    </div>
  );
}

export default ShowAppointment;
