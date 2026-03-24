import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from './LanguageContext';

function Account() {
  const { t } = useLanguage();
  const [accountData, setAccountData] = useState({});
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const role = localStorage.getItem('role');
    fetch(`/account?role=${role}`, { method: 'GET', headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
    .then(r => r.json())
    .then(data => { if (data.error) setMessage(data.error); else setAccountData(data); })
    .catch(() => setMessage(t.failedToLoad));
  }, [t.failedToLoad]);

  const handleLogout = () => { localStorage.removeItem('token'); localStorage.removeItem('username'); localStorage.removeItem('role'); navigate('/login'); };
  const handleBack = () => {
    const role = localStorage.getItem('role');
    navigate(role === 'patient' ? '/manageAppointment' : '/DoctorsAppointments');
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-50 flex items-center justify-center px-6 font-sans">
      <div className="w-full max-w-sm">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 text-center">{t.accountTitle}</h2>
        {message && <p className="mb-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2.5">{message}</p>}
        {accountData.full_name && (
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm mb-6">
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500">{t.fullName}</span>
                <span className="text-slate-800 font-medium">{accountData.full_name}</span>
              </div>
              <div className="border-t border-slate-100" />
              <div className="flex justify-between">
                <span className="text-slate-500">{t.username}</span>
                <span className="text-slate-800 font-medium">{accountData.username}</span>
              </div>
              <div className="border-t border-slate-100" />
              <div className="flex justify-between">
                <span className="text-slate-500">{t.email}</span>
                <span className="text-slate-800 font-medium">{accountData.email}</span>
              </div>
              {accountData.role === 'doctor' && (
                <>
                  <div className="border-t border-slate-100" />
                  <div className="flex justify-between">
                    <span className="text-slate-500">{t.specialization}</span>
                    <span className="text-slate-800 font-medium">{accountData.specialization}</span>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
        <button onClick={handleBack} className="w-full py-2.5 text-sm font-medium text-slate-600 bg-white border border-slate-300 hover:bg-slate-50 rounded-lg transition-colors">{t.back}</button>
        <button onClick={handleLogout} className="w-full mt-2 py-2 text-sm text-slate-500 hover:text-red-600 transition-colors">{t.signOut}</button>
      </div>
    </div>
  );
}

export default Account;
