import { useNavigate, NavLink, Link } from 'react-router-dom';
import { useLanguage } from '../LanguageContext';

export default function Navbar() {
  const { t } = useLanguage();
  const navigate = useNavigate();

  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');

  if (!token) return null;

  const dashboard = role === 'doctor' ? '/DoctorsAppointments' : '/ManageAppointment';

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('role');
    navigate('/login');
  };

  const navLinkClass = ({ isActive }) =>
    `text-sm font-medium transition-colors ${
      isActive
        ? 'text-blue-700 underline underline-offset-4'
        : 'text-slate-600 hover:text-slate-900'
    }`;

  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-14 bg-white border-b border-slate-200 flex items-center px-6">
      <Link
        to={dashboard}
        className="text-base font-bold text-blue-700 hover:text-blue-800 transition-colors mr-8 shrink-0"
      >
        MedBook
      </Link>

      <nav className="flex items-center gap-6 flex-1">
        {role === 'client' && (
          <>
            <NavLink to="/ShowAppointment" className={navLinkClass}>
              {t.myAppointments}
            </NavLink>
            <NavLink to="/Account" className={navLinkClass}>
              {t.account}
            </NavLink>
          </>
        )}
        {role === 'doctor' && (
          <>
            <NavLink to="/DoctorAvailability" className={navLinkClass}>
              {t.availability}
            </NavLink>
            <NavLink to="/Account" className={navLinkClass}>
              {t.account}
            </NavLink>
          </>
        )}
      </nav>

      <div className="flex items-center gap-3 shrink-0">
        <button
          onClick={handleLogout}
          className="text-sm font-medium text-slate-500 hover:text-red-500 transition-colors"
        >
          {t.signOut}
        </button>
      </div>
    </header>
  );
}
