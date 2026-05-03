import { useState } from 'react';
import client from '../api/client';
import { ACTIVITIES, EMOTIONS, type CheckInCreate } from '../utils/constants';

interface Props {
  onSuccess?: () => void;
}

export default function CheckInForm({ onSuccess }: Props) {
  const [energy, setEnergy] = useState<number | null>(null);
  const [focus, setFocus] = useState<number | null>(null);
  const [activity, setActivity] = useState<string>('');
  const [customActivity, setCustomActivity] = useState('');
  const [showCustom, setShowCustom] = useState(false);
  const [emotions, setEmotions] = useState<string[]>([]);
  const [note, setNote] = useState('');
  const [showSuccess, setShowSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);

  const toggleEmotion = (key: string) => {
    setEmotions(prev => prev.includes(key) ? prev.filter(e => e !== key) : [...prev, key]);
  };

  const effectiveActivity = showCustom ? customActivity.trim() : activity;

  const handleSubmit = async () => {
    if (!energy || !effectiveActivity) return;
    setLoading(true);
    try {
      const data: CheckInCreate = {
        energy_level: energy,
        focus_level: focus,
        activity: effectiveActivity,
        emotions: emotions.length > 0 ? emotions : null,
        note: note || null,
      };
      await client.post('/checkins/', data);
      setShowSuccess(true);
      setTimeout(() => {
        setShowSuccess(false);
        setEnergy(null); setFocus(null); setActivity(''); setCustomActivity('');
        setShowCustom(false); setEmotions([]); setNote(''); setStep(1);
        onSuccess?.();
      }, 2000);
    } catch (err) {
      console.error('Check-in failed:', err);
    } finally {
      setLoading(false);
    }
  };

  if (showSuccess) {
    return (
      <div className="card">
        <div className="checkin-success">
          <div className="success-check">✓</div>
          <h3 style={{ fontWeight: 600 }}>Check-in zapisany</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            Energia: {energy}/5 · {effectiveActivity}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Nowy Check-in</h2>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Krok {step}/3</span>
      </div>

      {step >= 1 && (
        <div className="form-group" style={{ marginBottom: '1.5rem' }}>
          <label className="form-label">Poziom energii</label>
          <div className="energy-buttons">
            {[1, 2, 3, 4, 5].map(level => (
              <button
                key={level}
                className={`energy-btn ${energy === level ? 'selected' : ''}`}
                data-level={level}
                onClick={() => { setEnergy(level); if (step === 1) setStep(2); }}
              >
                {level}
              </button>
            ))}
          </div>
        </div>
      )}

      {step >= 2 && (
        <div className="form-group" style={{ marginBottom: '1.5rem' }}>
          <label className="form-label">Ostatnia aktywność</label>
          <div className="activity-grid">
            {ACTIVITIES.map(act => (
              <button
                key={act.key}
                className={`activity-btn ${!showCustom && activity === act.key ? 'selected' : ''}`}
                onClick={() => { setActivity(act.key); setShowCustom(false); if (step === 2) setStep(3); }}
              >
                <span className="emoji">{act.emoji}</span>
                {act.label}
              </button>
            ))}
            <button
              className={`activity-btn ${showCustom ? 'selected' : ''}`}
              onClick={() => { setShowCustom(true); setActivity(''); if (step === 2) setStep(3); }}
            >
              <span className="emoji">✏️</span>
              Inne
            </button>
          </div>
          {showCustom && (
            <input
              className="input"
              style={{ marginTop: '0.5rem' }}
              type="text"
              placeholder="Wpisz swoją aktywność..."
              value={customActivity}
              onChange={e => setCustomActivity(e.target.value)}
              maxLength={50}
              autoFocus
            />
          )}
        </div>
      )}

      {step >= 3 && (
        <>
          <div className="form-group" style={{ marginBottom: '1rem' }}>
            <label className="form-label">Poziom fokusa</label>
            <div className="energy-buttons">
              {[1, 2, 3, 4, 5].map(level => (
                <button
                  key={level}
                  className={`energy-btn ${focus === level ? 'selected' : ''}`}
                  data-level={level}
                  onClick={() => setFocus(focus === level ? null : level)}
                  style={{ width: 44, height: 44, fontSize: '0.95rem' }}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          <div className="form-group" style={{ marginBottom: '1rem' }}>
            <label className="form-label">Emocje</label>
            <div className="emotion-tags">
              {EMOTIONS.map(em => (
                <button
                  key={em.key}
                  className={`emotion-tag ${emotions.includes(em.key) ? 'selected' : ''}`}
                  onClick={() => toggleEmotion(em.key)}
                >
                  {em.label}
                </button>
              ))}
            </div>
          </div>

          <div className="form-group" style={{ marginBottom: '1.5rem' }}>
            <label className="form-label">Notatka</label>
            <textarea
              className="textarea"
              placeholder="Opcjonalna notatka..."
              value={note}
              onChange={e => setNote(e.target.value)}
              maxLength={200}
            />
          </div>

          <button
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={!energy || !effectiveActivity || loading}
            style={{ width: '100%' }}
          >
            {loading ? 'Zapisuję...' : 'Zapisz Check-in'}
          </button>
        </>
      )}
    </div>
  );
}
