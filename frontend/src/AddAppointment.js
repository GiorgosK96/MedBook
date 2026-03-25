import { useState, useEffect } from 'react';
import { useLanguage } from './LanguageContext';

export const AddAppointment = () => {
  const { t } = useLanguage();
  const [date, setDate] = useState('');
  const [timeFrom, setTimeFrom] = useState('');
  const [timeTo, setTimeTo] = useState('');
  const [doctorId, setDoctorId] = useState('');
  const [comment, setComment] = useState('');
  const [message, setMessage] = useState('');
  const [isAccepted, setIsAccepted] = useState(null);
  const [doctors, setDoctors] = useState([]);

  useEffect(() => {
    fetch('/doctors', { method: 'GET', headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
    .then(r => r.json()).then(data => setDoctors(data.doctors))
    .catch(err => console.error('Error fetching doctors:', err));
  }, []);

  const handleSubmit = () => {
    if (!date || !timeFrom || !timeTo || !doctorId) { setMessage(t.allFieldsRequired); setIsAccepted(false); return; }
    fetch('/AddAppointment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ date, time_from: timeFrom, time_to: timeTo, doctor_id: doctorId, comments: comment }),
    })
    .then(r => r.json())
    .then(data => {
      if (data.error) { setMessage(`Error: ${data.error}`); setIsAccepted(false); }
      else { setMessage(data.message); setIsAccepted(true); setDate(''); setTimeFrom(''); setTimeTo(''); setDoctorId(''); setComment(''); }
    })
    .catch(() => { setMessage(t.errorOccurred); setIsAccepted(false); });
  };

  const inputClass = "w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/10 text-slate-800";

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-50 px-6 pb-10 pt-16 font-sans">
      <div className="max-w-md mx-auto">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 text-center">{t.addAppointmentTitle}</h2>
        <div className="bg-white border border-slate-200 rounded-xl p-7 shadow-sm space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.date}</label>
            <input type="date" value={date} onChange={(e) => setDate(e.target.value)} className={inputClass} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.from}</label>
              <input type="time" value={timeFrom} onChange={(e) => setTimeFrom(e.target.value)} className={inputClass} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.to}</label>
              <input type="time" value={timeTo} onChange={(e) => setTimeTo(e.target.value)} className={inputClass} />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.doctor}</label>
            <select value={doctorId} onChange={(e) => setDoctorId(e.target.value)} className={inputClass}>
              <option value="">{t.selectDoctor}</option>
              {doctors.map(d => <option key={d.id} value={d.id}>{d.full_name} ({d.specialization})</option>)}
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
        {message && (
          <p className={`mt-4 text-sm px-3 py-2.5 rounded-lg border ${isAccepted ? 'text-green-700 bg-green-50 border-green-200' : 'text-red-600 bg-red-50 border-red-200'}`}>{message}</p>
        )}
      </div>
    </div>
  );
};

export default AddAppointment;
