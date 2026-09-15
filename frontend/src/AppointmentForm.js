import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useLanguage } from './LanguageContext';
import { useToast } from './components/ToastContext';
import { formatTime, todayLocal } from './utils/formatDate';
import { endTimesFrom } from './utils/timeSlots';
import { apiFetch } from './utils/apiFetch';
import Spinner from './components/Spinner';

function AppointmentForm() {
  const { t } = useLanguage();
  const showToast = useToast();
  const navigate = useNavigate();
  const { appointmentId } = useParams();
  const [form, setForm] = useState({ doctor_id: '', date: '', time_from: '', time_to: '', comments: '' });
  const [doctors, setDoctors] = useState([]);
  const [slots, setSlots] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const update = (changes) => setForm(f => ({ ...f, ...changes }));

  useEffect(() => {
    const requests = [apiFetch('/doctors').then(r => r && r.json()).then(d => d && setDoctors(d.doctors))];
    if (appointmentId) {
      requests.push(apiFetch(`/ShowAppointment/${appointmentId}`).then(r => r && r.json()).then(d => {
        if (!d) return;
        if (d.error) { showToast(d.error, 'error'); navigate('/ShowAppointment'); return; }
        setForm({ doctor_id: String(d.doctor.id), date: d.date, time_from: d.time_from, time_to: d.time_to, comments: d.comments || '' });
      }));
    }
    Promise.all(requests)
      .catch(() => showToast(t.errorOccurred, 'error'))
      .finally(() => setLoading(false));
  }, [appointmentId, navigate, showToast, t.errorOccurred]);

  useEffect(() => {
    if (!form.doctor_id || !form.date) { setSlots(null); return; }
    let ignore = false;
    const params = new URLSearchParams({ date: form.date });
    if (appointmentId) params.set('exclude_appointment_id', appointmentId);
    apiFetch(`/doctors/${form.doctor_id}/availableSlots?${params}`)
      .then(r => r && r.json())
      .then(d => { if (!ignore && d) setSlots(d.slots || []); })
      .catch(() => showToast(t.errorOccurred, 'error'));
    return () => { ignore = true; };
  }, [form.doctor_id, form.date, appointmentId, showToast, t.errorOccurred]);

  const handleSubmit = () => {
    if (!form.doctor_id || !form.date || !form.time_from || !form.time_to) { showToast(t.allFieldsRequired, 'error'); return; }
    setSubmitting(true);
    apiFetch(appointmentId ? `/UpdateAppointment/${appointmentId}` : '/AddAppointment', {
      method: appointmentId ? 'PUT' : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    })
      .then(r => r && r.json())
      .then(d => {
        if (!d) return;
        if (d.error) { showToast(d.error, 'error'); return; }
        showToast(d.message, 'success');
        navigate('/ShowAppointment');
      })
      .catch(() => showToast(t.errorOccurred, 'error'))
      .finally(() => setSubmitting(false));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-50 flex items-center justify-center">
        <Spinner />
      </div>
    );
  }

  const grouped = {};
  doctors.forEach(d => {
    if (!grouped[d.specialization]) grouped[d.specialization] = [];
    grouped[d.specialization].push(d);
  });
  const endTimes = form.time_from && slots ? endTimesFrom(slots, form.time_from) : [];
  const inputClass = (disabled) => `w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/10 text-slate-800 ${disabled ? 'opacity-50' : ''}`;
  const labelClass = "block text-sm font-medium text-slate-600 mb-1.5";

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-50 flex items-center justify-center px-6 py-10 font-sans">
      <div className="w-full max-w-md">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 text-center">{appointmentId ? t.editAppointmentTitle : t.addAppointmentTitle}</h2>
        <div className="bg-white border border-slate-200 rounded-xl p-7 shadow-sm space-y-4">
          <div>
            <label className={labelClass}>{t.doctor}</label>
            <select value={form.doctor_id} onChange={(e) => update({ doctor_id: e.target.value, time_from: '', time_to: '' })} className={inputClass(false)}>
              <option value="">{t.selectDoctor}</option>
              {Object.keys(grouped).sort().map(spec => (
                <optgroup key={spec} label={spec}>
                  {grouped[spec].map(d => <option key={d.id} value={d.id}>{d.full_name}</option>)}
                </optgroup>
              ))}
            </select>
          </div>
          <div>
            <label className={labelClass}>{t.date}</label>
            <input type="date" value={form.date} min={todayLocal()} disabled={!form.doctor_id} onChange={(e) => update({ date: e.target.value, time_from: '', time_to: '' })} className={inputClass(!form.doctor_id)} />
            {!form.doctor_id && <p className="text-xs text-slate-400 mt-1">{t.selectDoctorFirst}</p>}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>{t.from}</label>
              <select value={form.time_from} disabled={!slots} onChange={(e) => update({ time_from: e.target.value, time_to: '' })} className={inputClass(!slots)}>
                <option value="">--</option>
                {slots && slots.map(s => <option key={s} value={s}>{formatTime(s)}</option>)}
              </select>
            </div>
            <div>
              <label className={labelClass}>{t.to}</label>
              <select value={form.time_to} disabled={!form.time_from} onChange={(e) => update({ time_to: e.target.value })} className={inputClass(!form.time_from)}>
                <option value="">--</option>
                {endTimes.map(s => <option key={s} value={s}>{formatTime(s)}</option>)}
              </select>
            </div>
          </div>
          {slots && slots.length === 0 && <p className="text-xs text-amber-600 text-center">{t.noSlotsAvailable}</p>}
          <div>
            <label className={labelClass}>{t.comments}</label>
            <textarea value={form.comments} onChange={(e) => update({ comments: e.target.value })} rows={3} className={`${inputClass(false)} resize-y`} />
          </div>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={submitting}
            className="w-full py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
          >
            {submitting ? '...' : appointmentId ? t.saveChanges : t.bookAppointment}
          </button>
        </div>
      </div>
    </div>
  );
}

export default AppointmentForm;
