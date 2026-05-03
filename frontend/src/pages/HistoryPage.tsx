import { useState, useEffect } from 'react';
import client from '../api/client';
import type { CheckIn } from '../utils/constants';
import { getActivityEmoji, getActivityLabel, getEnergyColor } from '../utils/constants';

export default function HistoryPage() {
  const [checkins, setCheckins] = useState<CheckIn[]>([]);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [loading, setLoading] = useState(true);

  const fetchCheckins = async () => {
    setLoading(true);
    try {
      const { data } = await client.get(`/checkins/?date=${selectedDate}`);
      setCheckins(data);
    } catch (err) {
      console.error('Failed to fetch history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchCheckins(); }, [selectedDate]);

  const handleDelete = async (id: number) => {
    if (!confirm('Usunąć ten check-in?')) return;
    try {
      await client.delete(`/checkins/${id}`);
      setCheckins(prev => prev.filter(c => c.id !== id));
    } catch (err) {
      console.error('Delete failed:', err);
    }
  };

  const formatTime = (ts: string) => {
    const d = new Date(ts);
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
  };

  return (
    <div>
      <div className="page-header">
        <h1>Historia</h1>
        <p>Przeglądaj i zarządzaj swoimi zapisami</p>
      </div>

      <div className="form-group" style={{ maxWidth: 220, marginBottom: '1.5rem' }}>
        <label className="form-label">Data</label>
        <input className="input" type="date" value={selectedDate} onChange={e => setSelectedDate(e.target.value)} />
      </div>

      {loading ? (
        <div className="empty-state"><p>Ładuję...</p></div>
      ) : checkins.length === 0 ? (
        <div className="empty-state">
          <p>Brak check-inów w dniu {selectedDate}</p>
        </div>
      ) : (
        <div className="history-list">
          {checkins.map(c => (
            <div key={c.id} className="history-item">
              <div className="history-energy" style={{ backgroundColor: getEnergyColor(c.energy_level) }}>
                {c.energy_level}
              </div>
              <div className="history-details">
                <div className="history-time">{formatTime(c.timestamp)}</div>
                <div className="history-activity">
                  {getActivityEmoji(c.activity)} {getActivityLabel(c.activity)}
                  {c.focus_level && <span> · Fokus: {c.focus_level}/5</span>}
                </div>
                {c.emotions && c.emotions.length > 0 && (
                  <div className="history-emotions">
                    {c.emotions.map(em => <span key={em} style={{ color: 'var(--text-muted)' }}>{em}</span>)}
                  </div>
                )}
                {c.note && <div className="history-note">"{c.note}"</div>}
              </div>
              <div className="history-actions">
                <button className="btn btn-danger btn-sm" onClick={() => handleDelete(c.id)}>Usuń</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
