import { Link } from 'react-router-dom';
import { useLanguage } from './LanguageContext';

function LandingPage() {
  const { t } = useLanguage();

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-50 flex flex-col items-center justify-center px-6 py-12 font-sans">
      <div className="w-full max-w-md text-center">
        <div className="mb-2">
          <span className="inline-block text-3xl font-bold text-blue-700 tracking-tight">{t.appName}</span>
        </div>
        <p className="text-sm text-slate-500 mb-10 max-w-xs mx-auto">
          {t.appTagline}
        </p>

        <div className="bg-white border border-slate-200 rounded-xl p-8 shadow-sm mb-8">
          <div className="mb-6">
            <p className="text-sm text-slate-500 mb-3">{t.newHere}</p>
            <Link to="/register">
              <button className="w-full py-2.5 px-4 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
                {t.createAccount}
              </button>
            </Link>
          </div>

          <div className="flex items-center gap-3 my-6">
            <div className="flex-1 h-px bg-slate-200" />
            <span className="text-xs text-slate-400">{t.or}</span>
            <div className="flex-1 h-px bg-slate-200" />
          </div>

          <div>
            <p className="text-sm text-slate-500 mb-3">{t.alreadyHaveAccount}</p>
            <Link to="/login">
              <button className="w-full py-2.5 px-4 text-sm font-medium text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 hover:border-slate-400 rounded-lg transition-colors">
                {t.signIn}
              </button>
            </Link>
          </div>
        </div>

      </div>
    </div>
  );
}

export default LandingPage;
