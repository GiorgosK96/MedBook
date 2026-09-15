export const TIME_SLOTS = [
  '08:00','08:30','09:00','09:30','10:00','10:30','11:00','11:30',
  '12:00','12:30','13:00','13:30','14:00','14:30','15:00','15:30',
  '16:00','16:30','17:00','17:30','18:00','18:30','19:00',
];

function addHalfHour(time) {
  const [h, m] = time.split(':').map(Number);
  const total = h * 60 + m + 30;
  return `${String(Math.floor(total / 60)).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`;
}

// End times run through consecutive free slots, stopping at the first taken one
export function endTimesFrom(freeSlots, start) {
  const ends = [];
  let slot = start;
  while (freeSlots.includes(slot)) {
    slot = addHalfHour(slot);
    ends.push(slot);
  }
  return ends;
}
