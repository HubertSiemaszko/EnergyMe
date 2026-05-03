// ── Types ──

export interface User {
  id: number;
  email: string;
  username: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface CheckIn {
  id: number;
  user_id: number;
  energy_level: number;
  focus_level: number | null;
  activity: string;
  emotions: string[] | null;
  note: string | null;
  timestamp: string;
}

export interface CheckInCreate {
  energy_level: number;
  focus_level?: number | null;
  activity: string;
  emotions?: string[] | null;
  note?: string | null;
  timestamp?: string | null;
}

export interface DailyInsight {
  date: string;
  avg_energy: number;
  avg_focus: number | null;
  peak_hour: string | null;
  peak_energy: number | null;
  low_hour: string | null;
  low_energy: number | null;
  total_checkins: number;
  recommendation: string;
}

export interface HeatmapCell {
  day_of_week: number;
  hour: number;
  avg_energy: number;
  count: number;
}

export interface CorrelationItem {
  activity: string;
  avg_energy: number;
  avg_focus: number | null;
  delta_energy: number;
  count: number;
  insight: string;
}

export interface EmotionCorrelation {
  emotion: string;
  avg_energy: number;
  avg_focus: number | null;
  count: number;
}

export interface CorrelationResponse {
  global_avg_energy: number;
  global_avg_focus: number | null;
  activity_correlations: CorrelationItem[];
  emotion_correlations: EmotionCorrelation[];
  top_booster: string | null;
  top_drainer: string | null;
}

export interface ScheduleBlock {
  hour: number;
  avg_energy: number;
  zone: 'high' | 'medium' | 'low';
  suggestion: string;
  emoji: string;
}

export interface ScheduleResponse {
  hourly: ScheduleBlock[];
  peak_block: string | null;
  dip_block: string | null;
  golden_hour: string | null;
  summary: string;
}

export interface TaskItem {
  name: string;
  duration_minutes: number;
  priority: 'high' | 'medium' | 'low';
}

export interface PlannedTask {
  name: string;
  start_hour: number;
  end_hour: number;
  zone: string;
  priority: string;
  reason: string;
}

export interface TaskPlanResponse {
  planned_tasks: PlannedTask[];
  unplanned_tasks: string[];
  summary: string;
}

// ── Constants ──

export interface ActivityDef {
  key: string;
  label: string;
  emoji: string;
}

export interface EmotionDef {
  key: string;
  label: string;
  emoji: string;
}

export const ACTIVITIES: ActivityDef[] = [
  { key: 'coffee', label: 'Kawa', emoji: '☕' },
  { key: 'meal', label: 'Posiłek', emoji: '🍽️' },
  { key: 'coding', label: 'Kodowanie', emoji: '💻' },
  { key: 'exercise', label: 'Ćwiczenia', emoji: '🏃' },
  { key: 'meeting', label: 'Spotkanie', emoji: '🤝' },
  { key: 'nap', label: 'Drzemka', emoji: '😴' },
  { key: 'reading', label: 'Czytanie', emoji: '📖' },
  { key: 'entertainment', label: 'Rozrywka', emoji: '🎮' },
  { key: 'meditation', label: 'Medytacja', emoji: '🧘' },
  { key: 'socializing', label: 'Rozmowy', emoji: '💬' },
];

export const EMOTIONS: EmotionDef[] = [
  { key: 'motivated', label: 'Zmotywowany', emoji: '🔥' },
  { key: 'calm', label: 'Spokojny', emoji: '😌' },
  { key: 'happy', label: 'Szczęśliwy', emoji: '😊' },
  { key: 'neutral', label: 'Neutralny', emoji: '😐' },
  { key: 'tired', label: 'Zmęczony', emoji: '😫' },
  { key: 'stressed', label: 'Zestresowany', emoji: '😤' },
  { key: 'anxious', label: 'Niespokojny', emoji: '😰' },
  { key: 'bored', label: 'Znudzony', emoji: '🥱' },
  { key: 'energized', label: 'Pełen energii', emoji: '⚡' },
  { key: 'sleepy', label: 'Senny', emoji: '😴' },
];

export const ENERGY_COLORS: Record<number, string> = {
  1: '#b55a4a', 2: '#c47a4a', 3: '#c49a6c', 4: '#7a9e6e', 5: '#5a8a7a',
};

export const ENERGY_LABELS: Record<number, string> = {
  1: 'Bardzo niska', 2: 'Niska', 3: 'Średnia', 4: 'Wysoka', 5: 'Bardzo wysoka',
};

export const DAY_NAMES = ['Pon', 'Wt', 'Śr', 'Czw', 'Pt', 'Sob', 'Nd'];

export function getActivityEmoji(key: string): string {
  return ACTIVITIES.find(a => a.key === key)?.emoji ?? '❓';
}

export function getActivityLabel(key: string): string {
  return ACTIVITIES.find(a => a.key === key)?.label ?? key;
}

export function getEmotionEmoji(key: string): string {
  return EMOTIONS.find(e => e.key === key)?.emoji ?? '❓';
}

export function getEnergyColor(level: number): string {
  return ENERGY_COLORS[level] ?? '#94a3b8';
}
