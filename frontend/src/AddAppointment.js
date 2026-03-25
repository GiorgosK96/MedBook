import { useState, useEffect } from 'react';
import { useLanguage } from './LanguageContext';
import { useToast } from './components/ToastContext';
import { formatSlot } from './utils/timeSlots';
import Spinner from './components/Spinner';

export const AddAppointment = () => {
  const { t } = useLanguage();
  const showToast = useToast();
  const [doctorId, setDoctorId] = useState('');
  const [date, setDate] = useState('');
  const [timeFrom, setTimeFrom] = useState('');
  const [timeTo, setTimeTo] = useState('');
  const [comment, setComment] = useState('');
  const [doctors, setDoctors] = useState([]);
  const [availableSlots, setAvailableSlots] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingSlots, setLoadingSlots] = useState(false);

  useEffect(() => {
    fetch('/doctors', { method: 'GET', headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
    .then(r => r.json()).then(data => setDoctors(data.doctors))
    .catch(() => showToast(t.errorOccurred, 'error'))
    .finally(() => setLoading(false));
  }, [t.errorOccurred, showToast]);

  useEffect(() => {
    if (!doctorId || !date) { setAvailableSlots(null); return; }
    setLoadingSlots(true);
    setTimeFrom(''); setTimeTo('');
    fetch(`/doctors/${doctorId}/availableSlots?date=${date}`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
      .then(r => r.json())
      .then(data => setAvailableSlots(data.slots))
      .catch(() => showToast(t.errorOccurred, 'error'))
      .finally(() => setLoadingSlots(false));
  }, [doctorId, date, showToast, t.errorOccurred]);

  const handleSubmit = () => {
    if (!date || !timeFrom || !timeTo || !doctorId) { showToast(t.allFieldsRequired, 'error'); return; }
    fetch('/AddAppointment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ date, time_from: timeFrom, time_to: timeTo, doctor_id: doctorId, comments: comment }),
    })
    .then(r => r.json())
    .then(data => {
      if (data.error) { showToast(`Error: ${data.error}`, 'error'); }
      else { showToast(data.message, 'success'); setDate(''); setTimeFrom(''); setTimeTo(''); setDoctorId(''); setComment(''); setAvailableSlots(null); }
    })
    .catch(() => showToast(t.errorOccurred, 'error'));
  };

  const inputClass = "w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/10 text-slate-800";

  const grouped = doctors.reduce((acc, d) => {
    (acc[d.specialization] = acc[d.specialization] || []).push(d);
    return acc;
  }, {});
  const specializations = Object.keys(grouped).sort();

  const toSlots = timeFrom && availableSlots ? availableSlots.filter(s => s > timeFrom) : [];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-50 flex items-center justify-center">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-50 flex items-center justify-center px-6 py-10 font-sans">
      <div className="w-full max-w-md">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 text-center">{t.addAppointmentTitle}</h2>
        <div className="bg-white border border-slate-200 rounded-xl p-7 shadow-sm space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.doctor}</label>
            <select value={doctorId} onChange={(e) => setDoctorId(e.target.value)} className={inputClass}>
              <option value="">{t.selectDoctor}</option>
              {specializations.map(spec => (
                <optgroup key={spec} label={spec}>
                  {grouped[spec].map(d => <option key={d.id} value={d.id}>{d.full_name}</option>)}
                </optgroup>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.date}</label>
            <input type="date" value={date} onChange={(e) => setDate(e.target.value)} min={new Date().toISOString().split('T')[0]} disabled={!doctorId} className={`${inputClass} ${!doctorId ? 'opacity-50' : ''}`} />
            {!doctorId && <p className="text-xs text-slate-400 mt-1">{t.selectDoctorFirst}</p>}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.from}</label>
              <select value={timeFrom} onChange={(e) => { setTimeFrom(e.target.value); setTimeTo(''); }} disabled={!availableSlots} className={`${inputClass} ${!availableSlots ? 'opacity-50' : ''}`}>
                <option value="">--</option>
                {availableSlots && availableSlots.map(s => <option key={s} value={s}>{formatSlot(s)}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.to}</label>
              <select value={timeTo} onChange={(e) => setTimeTo(e.target.value)} disabled={!timeFrom} className={`${inputClass} ${!timeFrom ? 'opacity-50' : ''}`}>
                <option value="">--</option>
                {toSlots.map(s => <option key={s} value={s}>{formatSlot(s)}</option>)}
              </select>
            </div>
          </div>
          {loadingSlots && <p className="text-xs text-slate-400 text-center">{t.selectDateFirst}...</p>}
          {availableSlots && availableSlots.length === 0 && <p className="text-xs text-amber-600 text-center">{t.noSlotsAvailable}</p>}
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.comments}</label>
            <textarea value={comment} onChange={(e) => setComment(e.target.value)} rows={3} className={`${inputClass} resize-y`} />
          </div>
          <button type="button" onClick={handleSubmit} className="w-full py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
            {t.bookAppointment}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddAppointment;
