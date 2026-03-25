import { useLanguage } from '../LanguageContext';

export default function ConfirmModal({ message, onConfirm, onCancel, confirmLabel, variant = 'danger' }) {
  const { t } = useLanguage();

  const btnClass = variant === 'success'
    ? 'bg-green-600 hover:bg-green-700'
    : 'bg-red-600 hover:bg-red-700';

  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center bg-black/40" onClick={onCancel}>
      <div
        className="bg-white rounded-xl p-6 max-w-sm w-full mx-4 shadow-lg animate-[fadeIn_0.15s_ease-out]"
        onClick={e => e.stopPropagation()}
      >
        <p className="text-sm text-slate-700 whitespace-pre-line leading-relaxed">{message}</p>
        <div className="flex gap-3 justify-end mt-6">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
          >
            {t.cancelBtn}
          </button>
          <button
            onClick={onConfirm}
            className={`px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors ${btnClass}`}
          >
            {confirmLabel || t.confirmDeleteBtn}
          </button>
        </div>
        <style>{`@keyframes fadeIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }`}</style>
      </div>
    </div>
  );
}
