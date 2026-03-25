import { useState, useEffect } from 'react';
import { useLanguage } from './LanguageContext';
import { useToast } from './components/ToastContext';
import Spinner from './components/Spinner';

function Account() {
  const { t } = useLanguage();
  const showToast = useToast();
  const [accountData, setAccountData] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const role = localStorage.getItem('role');
    fetch(`/account?role=${role}`, { method: 'GET', headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
    .then(r => r.json())
    .then(data => { if (data.error) showToast(data.error, 'error'); else setAccountData(data); })
    .catch(() => showToast(t.failedToLoad, 'error'))
    .finally(() => setLoading(false));
  }, [t.failedToLoad, showToast]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-50 flex items-center justify-center px-6 pt-16 font-sans">
      <div className="w-full max-w-sm">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 text-center">{t.accountTitle}</h2>
        {loading ? <Spinner /> : accountData.full_name && (
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
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
      </div>
    </div>
  );
}

export default Account;
