import { useState, useEffect, useMemo } from 'react';
import client from '../api/client';
import HeatMap from '../components/HeatMap';
import CorrelationChart from '../components/CorrelationChart';
import SmartScheduler from '../components/SmartScheduler';
import TaskPlanner from '../components/TaskPlanner';
import type { HeatmapCell, CorrelationResponse, ScheduleResponse } from '../utils/constants';

type RangeMode = 'preset' | 'custom';

export default function AnalyticsPage() {
  const [heatmapCells, setHeatmapCells] = useState<HeatmapCell[]>([]);
  const [correlations, setCorrelations] = useState<CorrelationResponse | null>(null);
  const [schedule, setSchedule] = useState<ScheduleResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'scheduler' | 'correlations' | 'heatmap' | 'planner'>('scheduler');

  // Date range
  const [rangeMode, setRangeMode] = useState<RangeMode>('preset');
  const [presetDays, setPresetDays] = useState(14);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const effectiveDays = useMemo(() => {
    if (rangeMode === 'custom' && startDate && endDate) {
      const diff = Math.ceil((new Date(endDate).getTime() - new Date(startDate).getTime()) / (1000 * 60 * 60 * 24));
      return Math.max(1, diff);
    }
    return presetDays;
  }, [rangeMode, presetDays, startDate, endDate]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = { days: effectiveDays };
      if (rangeMode === 'custom' && startDate) params.start = startDate;
      if (rangeMode === 'custom' && endDate) params.end = endDate;

      const [heatRes, corrRes, schedRes] = await Promise.all([
        client.get('/analytics/weekly', { params: { weeks: Math.max(1, Math.ceil(effectiveDays / 7)) } }),
        client.get('/analytics/correlations', { params }),
        client.get('/analytics/schedule', { params: { days: effectiveDays } }),
      ]);
      setHeatmapCells(heatRes.data.cells);
      setCorrelations(corrRes.data);
      setSchedule(schedRes.data);
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [effectiveDays, rangeMode]);

  return (
    <div>
      <div className="page-header">
        <h1>Analityka</h1>
        <p>Korelacje, wzorce i inteligentny planer dnia</p>
      </div>

      {/* Date range selector */}
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <button
            className={`btn ${rangeMode === 'preset' ? 'btn-primary' : 'btn-secondary'} btn-sm`}
            onClick={() => setRangeMode('preset')}
          >
            Szybki wybór
          </button>
          <button
            className={`btn ${rangeMode === 'custom' ? 'btn-primary' : 'btn-secondary'} btn-sm`}
            onClick={() => setRangeMode('custom')}
          >
            Własny zakres
          </button>
        </div>

        {rangeMode === 'preset' ? (
          <div className="tab-bar" style={{ maxWidth: 400 }}>
            {[7, 14, 30, 60, 90].map(d => (
              <button key={d} className={`tab-btn ${presetDays === d ? 'active' : ''}`} onClick={() => setPresetDays(d)}>
                {d} dni
              </button>
            ))}
          </div>
        ) : (
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <div className="form-group" style={{ minWidth: 150 }}>
              <label className="form-label">Od</label>
              <input className="input" type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
            </div>
            <div className="form-group" style={{ minWidth: 150 }}>
              <label className="form-label">Do</label>
              <input className="input" type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
            </div>
            <button className="btn btn-primary btn-sm" onClick={fetchData} style={{ marginTop: '1.25rem' }}
              disabled={!startDate || !endDate}
            >
              Analizuj
            </button>
            {startDate && endDate && (
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '1.25rem' }}>
                {effectiveDays} dni
              </span>
            )}
          </div>
        )}
      </div>

      {/* Section tabs */}
      <div className="tab-bar" style={{ maxWidth: 500, marginBottom: '1.5rem' }}>
        {([
          ['scheduler', 'Scheduler'],
          ['planner', 'Planer zadań'],
          ['correlations', 'Korelacje'],
          ['heatmap', 'Heatmapa'],
        ] as const).map(([key, label]) => (
          <button key={key} className={`tab-btn ${activeTab === key ? 'active' : ''}`} onClick={() => setActiveTab(key)}>
            {label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="empty-state"><p>Ładuję analizy...</p></div>
      ) : (
        <>
          {activeTab === 'scheduler' && schedule && <SmartScheduler data={schedule} />}
          {activeTab === 'planner' && <TaskPlanner days={effectiveDays} />}
          {activeTab === 'correlations' && correlations && <CorrelationChart data={correlations} />}
          {activeTab === 'heatmap' && <HeatMap cells={heatmapCells} />}
        </>
      )}
    </div>
  );
}
