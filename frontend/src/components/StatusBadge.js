import { useLanguage } from '../LanguageContext';

const STYLES = {
  pending: 'bg-amber-100 text-amber-700',
  confirmed: 'bg-green-100 text-green-700',
  declined: 'bg-red-100 text-red-700',
  cancelled: 'bg-slate-100 text-slate-500',
};

function StatusBadge({ status }) {
  const { t } = useLanguage();
  const labels = { pending: t.statusPending, confirmed: t.statusConfirmed, declined: t.statusDeclined, cancelled: t.statusCancelled };
  return <span className={`inline-block px-2 py-0.5 text-xs font-medium rounded-full ${STYLES[status]}`}>{labels[status]}</span>;
}

export default StatusBadge;
