import { useState, useEffect } from 'react';
import client from '../api/client';
import CheckInForm from '../components/CheckInForm';
import EnergyChart from '../components/EnergyChart';
import type { CheckIn, DailyInsight } from '../utils/constants';

export default function DashboardPage() {
  const [checkins, setCheckins] = useState<CheckIn[]>([]);
  const [insight, setInsight] = useState<DailyInsight | null>(null);
  const [loading, setLoading] = useState(true);

  const today = new Date().toISOString().split('T')[0];

  const fetchData = async () => {
    try {
      const [checkinsRes, insightRes] = await Promise.all([
        client.get(`/checkins/?date=${today}`),
        client.get(`/analytics/daily?date=${today}`),
      ]);
      setCheckins(checkinsRes.data);
      setInsight(insightRes.data);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Twój przegląd energii na dziś</p>
      </div>

      {insight && insight.total_checkins > 0 && (
        <div className="grid grid-4" style={{ marginBottom: '1.5rem' }}>
          <div className="stat-card">
            <div className="stat-value">{insight.avg_energy.toFixed(1)}</div>
            <div className="stat-label">Średnia energia</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{insight.peak_hour || '—'}</div>
            <div className="stat-label">Peak energy</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{insight.low_hour || '—'}</div>
            <div className="stat-label">Low energy</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{insight.total_checkins}</div>
            <div className="stat-label">Check-iny</div>
          </div>
        </div>
      )}

      <div className="grid grid-2">
        <CheckInForm onSuccess={fetchData} />
        <EnergyChart checkins={checkins} title={`Energia — ${today}`} />
      </div>

      {insight && insight.total_checkins > 0 && (
        <div className="insight-card" style={{ marginTop: '1.5rem' }}>
          <div className="insight-content">
            <h3>Dzienny wgląd</h3>
            <p>{insight.recommendation}</p>
          </div>
        </div>
      )}
    </div>
  );
}
