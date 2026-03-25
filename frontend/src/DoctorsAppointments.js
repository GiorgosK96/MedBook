import { useState, useEffect } from 'react';
import { useLanguage } from './LanguageContext';
import { formatDate, formatTime } from './utils/formatDate';

function DoctorsAppointments() {
  const { t, lang } = useLanguage();
  const [appointments, setAppointments] = useState([]);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetch('/doctorAppointments', { method: 'GET', headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
      .then(r => { if (r.ok) return r.json(); throw new Error(); })
      .then(data => setAppointments(data.appointments))
      .catch(() => setMessage(t.errorOccurred));
  }, [t.errorOccurred]);

  const handleDelete = (id) => {
    if (!window.confirm(t.confirmDelete)) return;
    fetch(`/doctorAppointments/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
      .then(r => { if (r.ok) r.json().then(d => { setMessage(d.message); setAppointments(appointments.filter(a => a.id !== id)); }); else r.json().then(d => setMessage(d.message)); })
      .catch(() => setMessage(t.errorOccurred));
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-50 px-6 pb-10 pt-16 font-sans">
      <div className="max-w-xl mx-auto">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 text-center">{t.doctorAppointmentsTitle}</h2>

        {appointments.length === 0 && !message ? (
          <div className="text-center py-16 bg-white border border-slate-200 rounded-xl shadow-sm mb-6">
            <p className="text-3xl mb-3 opacity-40">🩺</p>
            <p className="text-base font-semibold text-slate-800 mb-1">{t.noAppointmentsScheduled}</p>
            <p className="text-sm text-slate-500">{t.noAppointmentsScheduledDesc}</p>
          </div>
        ) : (
          <div className="space-y-3 mb-6">
            {appointments.map(a => (
              <div key={a.id} className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <div className="grid grid-cols-[100px_1fr] gap-y-1.5 text-sm">
                  <span className="font-medium text-slate-500">{t.patientName}</span>
                  <span className="text-slate-800">{a.patient.full_name}</span>
                  <span className="font-medium text-slate-500">{t.email}</span>
                  <span className="text-slate-800">{a.patient.email}</span>
                  <span className="font-medium text-slate-500">{t.date}</span>
                  <span className="text-slate-800">{formatDate(a.date, lang)}</span>
                  <span className="font-medium text-slate-500">{t.time}</span>
                  <span className="text-slate-800">{formatTime(a.time_from)} – {formatTime(a.time_to)}</span>
                  {a.comments && (<><span className="font-medium text-slate-500">{t.notes}</span><span className="text-slate-800">{a.comments}</span></>)}
                </div>
                <div className="mt-4 pt-3 border-t border-slate-100">
                  <button onClick={() => handleDelete(a.id)} className="px-3 py-1.5 text-xs font-medium text-red-600 border border-red-600 rounded-md hover:bg-red-50 transition-colors">{t.cancelAppointment}</button>
                </div>
              </div>
            ))}
          </div>
        )}

        {message && <p className="mt-4 text-sm text-blue-700 bg-blue-50 border border-blue-200 rounded-lg px-3 py-2.5">{message}</p>}
      </div>
    </div>
  );
}

export default DoctorsAppointments;
