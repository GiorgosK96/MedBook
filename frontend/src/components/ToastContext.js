import { createContext, useContext, useState, useCallback } from 'react';

const ToastContext = createContext();

const ICONS = {
  success: (
    <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  ),
  error: (
    <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  ),
  info: (
    <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
      <circle cx="12" cy="12" r="10" />
      <path strokeLinecap="round" d="M12 16v-4M12 8h.01" />
    </svg>
  ),
};

const STYLES = {
  success: 'bg-green-50 text-green-700 border-green-200',
  error: 'bg-red-50 text-red-600 border-red-200',
  info: 'bg-blue-50 text-blue-700 border-blue-200',
};

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((message, type = 'info') => {
    const id = Date.now() + Math.random();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 3500);
  }, []);

  const dismiss = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={showToast}>
      {children}
      {toasts.length > 0 && (
        <div className="fixed bottom-16 right-4 z-[60] flex flex-col gap-2 max-w-xs">
          {toasts.map(toast => (
            <div
              key={toast.id}
              onClick={() => dismiss(toast.id)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border rounded-lg shadow-md cursor-pointer
                animate-[slideUp_0.25s_ease-out] ${STYLES[toast.type]}`}
            >
              {ICONS[toast.type]}
              <span>{toast.message}</span>
            </div>
          ))}
          <style>{`@keyframes slideUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }`}</style>
        </div>
      )}
    </ToastContext.Provider>
  );
}

export function useToast() {
  return useContext(ToastContext);
}
