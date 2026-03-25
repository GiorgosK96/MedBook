import { useState, useEffect } from 'react';
import { useLanguage } from './LanguageContext';
import { useToast } from './components/ToastContext';
import Spinner from './components/Spinner';

function Account() {
  const { t } = useLanguage();
  const showToast = useToast();
  const [accountData, setAccountData] = useState({});
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({ full_name: '', email: '', current_password: '', new_password: '' });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const role = localStorage.getItem('role');
    fetch(`/account?role=${role}`, { method: 'GET', headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
    .then(r => r.json())
    .then(data => { if (data.error) showToast(data.error, 'error'); else setAccountData(data); })
    .catch(() => showToast(t.failedToLoad, 'error'))
    .finally(() => setLoading(false));
  }, [t.failedToLoad, showToast]);

  const startEditing = () => {
    setForm({ full_name: accountData.full_name, email: accountData.email, current_password: '', new_password: '' });
    setEditing(true);
  };

  const cancelEditing = () => {
    setEditing(false);
  };

  const handleSave = () => {
    if (!form.full_name.trim() || !form.email.trim()) {
      showToast(t.allFieldsRequired, 'error');
      return;
    }
    setSaving(true);
    fetch('/account', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({
        role: localStorage.getItem('role'),
        full_name: form.full_name.trim(),
        email: form.email.trim(),
        ...(form.new_password ? { current_password: form.current_password, new_password: form.new_password } : {}),
      }),
    })
    .then(r => r.json().then(data => ({ ok: r.ok, data })))
    .then(({ ok, data }) => {
      if (ok) {
        setAccountData(data);
        setEditing(false);
        showToast(t.profileUpdated, 'success');
      } else {
        showToast(data.error, 'error');
      }
    })
    .catch(() => showToast(t.errorOccurred, 'error'))
    .finally(() => setSaving(false));
  };

  const inputClass = "w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/10 text-slate-800";

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-50 flex items-center justify-center px-6 pt-16 font-sans">
      <div className="w-full max-w-sm">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 text-center">{t.accountTitle}</h2>

        {loading ? <Spinner /> : !accountData.full_name ? null : editing ? (
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.fullName}</label>
              <input type="text" value={form.full_name} onChange={e => setForm({ ...form, full_name: e.target.value })} className={inputClass} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.email}</label>
              <input type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} className={inputClass} />
            </div>

            <div className="border-t border-slate-100 pt-4">
              <div className="mb-3">
                <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.currentPassword}</label>
                <input type="password" value={form.current_password} onChange={e => setForm({ ...form, current_password: e.target.value })} className={inputClass} />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.newPassword}</label>
                <input type="password" value={form.new_password} onChange={e => setForm({ ...form, new_password: e.target.value })} className={inputClass} />
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <button
                onClick={cancelEditing}
                className="flex-1 py-2.5 text-sm font-medium text-slate-600 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
              >
                {t.cancelBtn}
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="flex-1 py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
              >
                {t.saveChanges}
              </button>
            </div>
          </div>
        ) : (
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
            <button
              onClick={startEditing}
              className="w-full mt-5 py-2.5 text-sm font-medium text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
            >
              {t.editProfile}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default Account;
