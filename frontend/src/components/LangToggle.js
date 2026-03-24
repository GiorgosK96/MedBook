import { useLanguage } from '../LanguageContext';

export default function LangToggle() {
  const { lang, toggleLang } = useLanguage();
  return (
    <button
      onClick={toggleLang}
      className="fixed top-4 right-4 px-3 py-1.5 text-xs font-medium bg-white border border-slate-300 rounded-full text-slate-600 hover:bg-slate-50 transition-colors shadow-sm z-50"
    >
      {lang === 'en' ? 'GR' : 'EN'}
    </button>
  );
}
