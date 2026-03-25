import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from './LanguageContext';
import { formatDate, formatTime } from './utils/formatDate';

function ShowAppointment() {
  const { t, lang } = useLanguage();
  const [appointments, setAppointments] = useState([]);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetch('/ShowAppointment', { method: 'GET', headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
      .then(r => { if (r.ok) return r.json(); throw new Error(); })
      .then(data => setAppointments(data.appointments))
      .catch(() => setMessage(t.errorOccurred));
  }, [t.errorOccurred]);

  const handleDelete = (id) => {
    if (!window.confirm(t.confirmDelete)) return;
    fetch(`/ShowAppointment/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
      .then(r => { if (r.ok) r.json().then(d => { setMessage(d.message); setAppointments(appointments.filter(a => a.id !== id)); }); else r.json().then(d => setMessage(d.message)); })
      .catch(() => setMessage(t.errorOccurred));
  };

  const handleLogout = () => { localStorage.removeItem('token'); localStorage.removeItem('username'); localStorage.removeItem('role'); navigate('/login'); };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-50 px-6 py-10 font-sans">
      <div className="max-w-xl mx-auto">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 text-center">{t.yourAppointments}</h2>

        {appointments.length === 0 && !message ? (
          <div className="text-center py-16 bg-white border border-slate-200 rounded-xl shadow-sm mb-6">
            <p className="text-3xl mb-3 opacity-40">📅</p>
            <p className="text-base font-semibold text-slate-800 mb-1">{t.noAppointmentsYet}</p>
            <p className="text-sm text-slate-500">{t.noAppointmentsDesc}</p>
          </div>
        ) : (
          <div className="space-y-3 mb-6">
            {appointments.map(a => (
              <div key={a.id} className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <div className="grid grid-cols-[80px_1fr] gap-y-1.5 text-sm">
                  <span className="font-medium text-slate-500">{t.date}</span>
                  <span className="text-slate-800">{formatDate(a.date, lang)}</span>
                  <span className="font-medium text-slate-500">{t.time}</span>
                  <span className="text-slate-800">{formatTime(a.time_from)} – {formatTime(a.time_to)}</span>
                  <span className="font-medium text-slate-500">{t.doctor}</span>
                  <span className="text-slate-800">{a.doctor.full_name} ({a.doctor.specialization})</span>
                  {a.comments && (<><span className="font-medium text-slate-500">{t.notes}</span><span className="text-slate-800">{a.comments}</span></>)}
                </div>
                <div className="flex gap-2 mt-4 pt-3 border-t border-slate-100">
                  <button onClick={() => navigate(`/UpdateAppointment/${a.id}`)} className="px-3 py-1.5 text-xs font-medium text-blue-600 border border-blue-600 rounded-md hover:bg-blue-50 transition-colors">{t.edit}</button>
                  <button onClick={() => handleDelete(a.id)} className="px-3 py-1.5 text-xs font-medium text-red-600 border border-red-600 rounded-md hover:bg-red-50 transition-colors">{t.delete}</button>
                </div>
              </div>
            ))}
          </div>
        )}

        <button onClick={() => navigate('/ManageAppointment')} className="w-full py-2.5 text-sm font-medium text-slate-600 bg-white border border-slate-300 hover:bg-slate-50 rounded-lg transition-colors">{t.backToDashboard}</button>
        <button onClick={handleLogout} className="w-full mt-2 py-2 text-sm text-slate-500 hover:text-red-600 transition-colors">{t.signOut}</button>
        {message && <p className="mt-4 text-sm text-blue-700 bg-blue-50 border border-blue-200 rounded-lg px-3 py-2.5">{message}</p>}
      </div>
    </div>
  );
}

export default ShowAppointment;
