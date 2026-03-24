import { useNavigate } from 'react-router-dom';
import { useLanguage } from './LanguageContext';

function ManageAppointment() {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const username = localStorage.getItem('username');

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('role');
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-50 flex items-center justify-center px-6 font-sans">
      <div className="w-full max-w-sm text-center">
        <span className="text-xl font-bold text-blue-700">{t.appName}</span>
        <h2 className="text-lg font-semibold text-slate-800 mt-6 mb-1">{t.dashboard}</h2>
        <p className="text-sm text-slate-500 mb-8">
          {username ? `${t.welcomeBack}, ${username}` : t.manageAppointments}
        </p>

        <div className="space-y-3">
          <button onClick={() => navigate('/AddAppointment')} className="w-full py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
            {t.newAppointment}
          </button>
          <button onClick={() => navigate('/ShowAppointment')} className="w-full py-2.5 text-sm font-medium text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 hover:border-slate-400 rounded-lg transition-colors">
            {t.myAppointments}
          </button>
          <button onClick={() => navigate('/account')} className="w-full py-2.5 text-sm font-medium text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 hover:border-slate-400 rounded-lg transition-colors">
            {t.account}
          </button>
          <button onClick={handleLogout} className="w-full mt-2 py-2.5 text-sm font-medium text-slate-500 hover:text-red-600 transition-colors">
            {t.signOut}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ManageAppointment;
