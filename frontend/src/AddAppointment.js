import { useState, useEffect } from 'react';
import { useLanguage } from './LanguageContext';
import { useToast } from './components/ToastContext';
import Spinner from './components/Spinner';

const TIME_SLOTS = [
  '08:00','08:30','09:00','09:30','10:00','10:30','11:00','11:30',
  '12:00','12:30','13:00','13:30','14:00','14:30','15:00','15:30',
  '16:00','16:30','17:00','17:30','18:00','18:30','19:00',
];

function formatSlot(t) {
  const [h, m] = t.split(':');
  const d = new Date(); d.setHours(+h, +m);
  return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
}

export const AddAppointment = () => {
  const { t } = useLanguage();
  const showToast = useToast();
  const [date, setDate] = useState('');
  const [timeFrom, setTimeFrom] = useState('');
  const [timeTo, setTimeTo] = useState('');
  const [doctorId, setDoctorId] = useState('');
  const [comment, setComment] = useState('');
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/doctors', { method: 'GET', headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
    .then(r => r.json()).then(data => setDoctors(data.doctors))
    .catch(() => showToast(t.errorOccurred, 'error'))
    .finally(() => setLoading(false));
  }, [t.errorOccurred, showToast]);

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
      else { showToast(data.message, 'success'); setDate(''); setTimeFrom(''); setTimeTo(''); setDoctorId(''); setComment(''); }
    })
    .catch(() => showToast(t.errorOccurred, 'error'));
  };

  const inputClass = "w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/10 text-slate-800";

  const grouped = doctors.reduce((acc, d) => {
    (acc[d.specialization] = acc[d.specialization] || []).push(d);
    return acc;
  }, {});
  const specializations = Object.keys(grouped).sort();

  const toSlots = timeFrom ? TIME_SLOTS.filter(s => s > timeFrom) : TIME_SLOTS;

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
            <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.date}</label>
            <input type="date" value={date} onChange={(e) => setDate(e.target.value)} min={new Date().toISOString().split('T')[0]} className={inputClass} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.from}</label>
              <select value={timeFrom} onChange={(e) => { setTimeFrom(e.target.value); setTimeTo(''); }} className={inputClass}>
                <option value="">--</option>
                {TIME_SLOTS.map(s => <option key={s} value={s}>{formatSlot(s)}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.to}</label>
              <select value={timeTo} onChange={(e) => setTimeTo(e.target.value)} className={inputClass}>
                <option value="">--</option>
                {toSlots.map(s => <option key={s} value={s}>{formatSlot(s)}</option>)}
              </select>
            </div>
          </div>
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
