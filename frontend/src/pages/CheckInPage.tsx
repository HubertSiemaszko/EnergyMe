import { useNavigate } from 'react-router-dom';
import CheckInForm from '../components/CheckInForm';

export default function CheckInPage() {
  const navigate = useNavigate();

  return (
    <div>
      <div className="page-header">
        <h1>Nowy Check-in</h1>
        <p>Jak się teraz czujesz? Zapisz swój poziom energii.</p>
      </div>
      <div style={{ maxWidth: 560 }}>
        <CheckInForm onSuccess={() => navigate('/')} />
      </div>
    </div>
  );
}
