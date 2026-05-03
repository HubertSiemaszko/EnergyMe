import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../api/client';
import axios from 'axios';

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [demoLoading, setDemoLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const endpoint = isRegister ? '/auth/register' : '/auth/login';
      const body = isRegister ? { email, username, password } : { email, password };
      const { data } = await client.post(endpoint, body);
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      navigate('/');
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'Wystąpił błąd');
      } else {
        setError('Wystąpił błąd');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDemo = async () => {
    setDemoLoading(true);
    setError('');
    try {
      await client.post('/demo/seed');
      const { data } = await client.post('/auth/login', {
        email: 'demo@energymap.com',
        password: 'demo123',
      });
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      navigate('/');
    } catch (err) {
      setError('Nie udało się załadować danych demo');
    } finally {
      setDemoLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-title">EnergyMe</div>
        <p className="login-subtitle">Odkryj swój naturalny rytm energii</p>

        {error && <div className="login-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group" style={{ marginBottom: '1rem' }}>
            <label className="form-label">Email</label>
            <input className="input" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="twoj@email.com" required />
          </div>
          {isRegister && (
            <div className="form-group" style={{ marginBottom: '1rem' }}>
              <label className="form-label">Nazwa użytkownika</label>
              <input className="input" type="text" value={username} onChange={e => setUsername(e.target.value)} placeholder="jan_kowalski" required />
            </div>
          )}
          <div className="form-group" style={{ marginBottom: '1.5rem' }}>
            <label className="form-label">Hasło</label>
            <input className="input" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••" required />
          </div>
          <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: '100%', marginBottom: '0.75rem' }}>
            {loading ? 'Ładuję...' : isRegister ? 'Zarejestruj się' : 'Zaloguj się'}
          </button>
        </form>

        <button className="btn btn-secondary" onClick={() => { setIsRegister(!isRegister); setError(''); }} style={{ width: '100%', marginBottom: '1.5rem' }}>
          {isRegister ? 'Masz już konto? Zaloguj się' : 'Nie masz konta? Zarejestruj się'}
        </button>

        <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.75rem', margin: '0 0 1rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>lub</div>

        <button className="btn btn-primary" onClick={handleDemo} disabled={demoLoading} style={{ width: '100%' }}>
          {demoLoading ? 'Ładuję dane demo...' : 'Tryb Demo — 14 dni danych'}
        </button>
      </div>
    </div>
  );
}
