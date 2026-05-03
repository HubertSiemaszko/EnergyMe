import { useState } from 'react';
import type { ScheduleResponse, ScheduleBlock } from '../utils/constants';

interface Props {
  data: ScheduleResponse;
}

export default function SmartScheduler({ data }: Props) {
  const { hourly, peak_block, dip_block, golden_hour, summary } = data;
  const [expandedHour, setExpandedHour] = useState<number | null>(null);

  if (hourly.length === 0) {
    return (
      <div className="card">
        <h3 className="card-title">Smart Scheduler</h3>
        <div className="empty-state">
          <p>Za mało danych. Dodawaj check-iny, aby otrzymać plan dnia.</p>
        </div>
      </div>
    );
  }

  const lowEnergyHours = hourly.filter(b => b.tips && b.tips.length > 0);

  return (
    <div className="card">
      <h3 className="card-title" style={{ marginBottom: '0.5rem' }}>Smart Scheduler</h3>

      <div className="insight-card" style={{ marginBottom: '1.5rem' }}>
        <div className="insight-content">
          <h3>Rekomendacja dnia</h3>
          <p>{summary}</p>
        </div>
      </div>

      <div className="grid grid-3" style={{ marginBottom: '1.5rem' }}>
        {golden_hour && (
          <div className="stat-card">
            <div className="stat-value">{golden_hour}</div>
            <div className="stat-label">Złota godzina</div>
          </div>
        )}
        {peak_block && (
          <div className="stat-card">
            <div className="stat-value" style={{ fontSize: '1.2rem', color: 'var(--energy-4)' }}>{peak_block}</div>
            <div className="stat-label">Deep work</div>
          </div>
        )}
        {dip_block && (
          <div className="stat-card">
            <div className="stat-value" style={{ fontSize: '1.2rem', color: 'var(--energy-1)' }}>{dip_block}</div>
            <div className="stat-label">Przerwa</div>
          </div>
        )}
      </div>

      {/* Remedial tips section */}
      {lowEnergyHours.length > 0 && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h4 style={{ fontSize: '0.78rem', fontWeight: 500, marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>
            Sugestie na godziny niskiej energii
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            {lowEnergyHours.map(block => (
              <div key={block.hour} className="insight-card" style={{
                borderLeftColor: 'var(--energy-1)',
                padding: '0.75rem 1rem',
              }}>
                <div className="insight-content">
                  <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span>{block.hour.toString().padStart(2, '0')}:00</span>
                    <span style={{ fontSize: '0.72rem', fontWeight: 400, color: 'var(--text-muted)' }}>
                      energia {block.avg_energy.toFixed(1)}/5
                    </span>
                  </h3>
                  <ul style={{ margin: '0.3rem 0 0', paddingLeft: '1rem', fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                    {block.tips!.map((tip, i) => (
                      <li key={i}>{tip}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <h4 style={{ fontSize: '0.78rem', fontWeight: 500, marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>
        Optymalny plan dnia
      </h4>
      <div className="schedule-timeline">
        {hourly.map(block => (
          <div key={block.hour}>
            <div
              className={`schedule-block ${block.zone}`}
              style={{ cursor: block.tips ? 'pointer' : 'default' }}
              onClick={() => block.tips && setExpandedHour(expandedHour === block.hour ? null : block.hour)}
            >
              <span className="schedule-hour">{block.hour.toString().padStart(2, '0')}:00</span>
              <span className="schedule-suggestion">{block.suggestion}</span>
              {block.tips && (
                <span style={{ fontSize: '0.7rem', color: 'var(--accent)', marginLeft: '0.25rem' }}>
                  {expandedHour === block.hour ? '▲' : '▼'}
                </span>
              )}
              <span style={{
                marginLeft: 'auto', fontSize: '0.75rem', fontWeight: 600,
                color: block.zone === 'high' ? 'var(--energy-4)' : block.zone === 'medium' ? 'var(--energy-3)' : 'var(--energy-1)',
              }}>
                {block.avg_energy.toFixed(1)}
              </span>
            </div>
            {expandedHour === block.hour && block.tips && (
              <div style={{
                padding: '0.5rem 1rem 0.5rem 4rem',
                fontSize: '0.78rem', color: 'var(--text-secondary)',
                background: 'rgba(196,154,108,0.05)',
                borderLeft: '2px solid var(--accent)',
                borderRadius: '0 0 var(--radius-sm) var(--radius-sm)',
              }}>
                <div style={{ fontWeight: 500, fontSize: '0.72rem', color: 'var(--accent)', marginBottom: '0.3rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Co historycznie pomaga:
                </div>
                {block.tips.map((tip, i) => (
                  <div key={i} style={{ marginBottom: '0.15rem' }}>• {tip}</div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
