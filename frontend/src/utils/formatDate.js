export function formatDate(dateStr, lang = 'en') {
  const date = new Date(dateStr + 'T00:00:00');
  return date.toLocaleDateString(lang === 'el' ? 'el-GR' : 'en-GB', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

export function formatTime(timeStr) {
  const [h, m] = timeStr.split(':');
  const date = new Date();
  date.setHours(parseInt(h), parseInt(m));
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
}
