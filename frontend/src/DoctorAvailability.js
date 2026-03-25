import { useState, useEffect } from 'react';
import { useLanguage } from './LanguageContext';
import { useToast } from './components/ToastContext';
import { TIME_SLOTS, formatSlot } from './utils/timeSlots';
import Spinner from './components/Spinner';

function DoctorAvailability() {
  const { t } = useLanguage();
  const showToast = useToast();
  const [availability, setAvailability] = useState(Array.from({ length: 7 }, () => []));
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const dayNames = [t.monday, t.tuesday, t.wednesday, t.thursday, t.friday, t.saturday, t.sunday];

  useEffect(() => {
    fetch('/doctorAvailability', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
      .then(r => r.json())
      .then(data => {
        const grouped = Array.from({ length: 7 }, () => []);
        (data.availability || []).forEach(s => {
          grouped[s.day_of_week].push({ start_time: s.start_time, end_time: s.end_time });
        });
        setAvailability(grouped);
      })
      .catch(() => showToast(t.errorOccurred, 'error'))
      .finally(() => setLoading(false));
  }, [t.errorOccurred, showToast]);

  const addWindow = (dayIdx) => {
    const updated = availability.map((day, i) =>
      i === dayIdx ? [...day, { start_time: '09:00', end_time: '17:00' }] : day
    );
    setAvailability(updated);
  };

  const removeWindow = (dayIdx, slotIdx) => {
    const updated = availability.map((day, i) =>
      i === dayIdx ? day.filter((_, j) => j !== slotIdx) : day
    );
    setAvailability(updated);
  };

  const updateWindow = (dayIdx, slotIdx, field, value) => {
    const updated = availability.map((day, i) =>
      i === dayIdx ? day.map((s, j) => j === slotIdx ? { ...s, [field]: value } : s) : day
    );
    setAvailability(updated);
  };

  const handleSave = () => {
    const flat = [];
    for (let day = 0; day < 7; day++) {
      for (const s of availability[day]) {
        if (s.start_time >= s.end_time) {
          showToast(`${dayNames[day]}: ${t.from} < ${t.to}`, 'error');
          return;
        }
        flat.push({ day_of_week: day, start_time: s.start_time, end_time: s.end_time });
      }
    }
    setSaving(true);
    fetch('/doctorAvailability', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ availability: flat }),
    })
      .then(r => r.json().then(d => ({ ok: r.ok, d })))
      .then(({ ok, d }) => {
        if (ok) showToast(t.availabilitySaved, 'success');
        else showToast(d.error, 'error');
      })
      .catch(() => showToast(t.errorOccurred, 'error'))
      .finally(() => setSaving(false));
  };

  const inputClass = "px-2 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/10 text-slate-800";

  // End time slots filtered to be after start_time
  const endSlots = (startTime) => TIME_SLOTS.filter(s => s > startTime);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-50 flex items-center justify-center">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-50 px-6 pb-10 pt-16 font-sans">
      <div className="max-w-lg mx-auto">
        <h2 className="text-lg font-semibold text-slate-800 mb-6 text-center">{t.availabilityTitle}</h2>

        <div className="space-y-3">
          {dayNames.map((name, dayIdx) => (
            <div key={dayIdx} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-slate-700">{name}</span>
                <button
                  onClick={() => addWindow(dayIdx)}
                  className="text-xs font-medium text-blue-600 hover:text-blue-700 transition-colors"
                >
                  + {t.addTimeWindow}
                </button>
              </div>

              {availability[dayIdx].length === 0 ? (
                <p className="text-xs text-slate-400 italic">—</p>
              ) : (
                <div className="space-y-2">
                  {availability[dayIdx].map((slot, slotIdx) => (
                    <div key={slotIdx} className="flex items-center gap-2">
                      <select
                        value={slot.start_time}
                        onChange={e => updateWindow(dayIdx, slotIdx, 'start_time', e.target.value)}
                        className={inputClass}
                      >
                        {TIME_SLOTS.map(s => <option key={s} value={s}>{formatSlot(s)}</option>)}
                      </select>
                      <span className="text-xs text-slate-400">–</span>
                      <select
                        value={slot.end_time}
                        onChange={e => updateWindow(dayIdx, slotIdx, 'end_time', e.target.value)}
                        className={inputClass}
                      >
                        {endSlots(slot.start_time).map(s => <option key={s} value={s}>{formatSlot(s)}</option>)}
                      </select>
                      <button
                        onClick={() => removeWindow(dayIdx, slotIdx)}
                        className="text-xs text-red-500 hover:text-red-700 transition-colors ml-1"
                      >
                        {t.remove}
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full mt-6 py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
        >
          {t.saveChanges}
        </button>
      </div>
    </div>
  );
}

export default DoctorAvailability;
