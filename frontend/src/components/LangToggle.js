import { useLanguage } from '../LanguageContext';

export default function LangToggle() {
  const { lang, toggleLang } = useLanguage();
  return (
    <button
      onClick={toggleLang}
      className="fixed bottom-4 right-4 z-50 px-3 py-1.5 text-xs font-medium bg-white border border-slate-300 rounded-full text-slate-600 hover:bg-slate-50 transition-colors shadow-sm"
    >
      {lang === 'en' ? 'GR' : 'EN'}
    </button>
  );
}
