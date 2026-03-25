import { useState } from 'react';
import { useNavigate } from "react-router-dom";
import { useLanguage } from './LanguageContext';

function Login() {
  const { t } = useLanguage();
  const [formData, setFormData] = useState({ email: '', password: '', role: 'patient' });
  const [message, setMessage] = useState('');
  const [errors, setErrors] = useState({});
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.email) newErrors.email = t.emailRequired;
    if (!formData.password) newErrors.password = t.passwordRequired;
    return newErrors;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) { setErrors(newErrors); return; }
    fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) { setMessage(data.error); }
        else {
          setMessage(data.message);
          if (data.token) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('username', data.username);
            localStorage.setItem('role', data.role);
            navigate(data.role === 'patient' ? "/ManageAppointment" : "/DoctorsAppointments");
          }
        }
      })
      .catch(() => setMessage(t.errorOccurred));
  };

  const inputClass = "w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/10 text-slate-800";

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-50 flex items-center justify-center px-6 font-sans">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <span className="text-2xl font-bold text-blue-700">{t.appName}</span>
        </div>
        <h2 className="text-lg font-semibold text-slate-800 mb-5 text-center">{t.signInTitle}</h2>

        <form onSubmit={handleSubmit} noValidate className="bg-white border border-slate-200 rounded-xl p-7 shadow-sm space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.email}</label>
            <input type="email" name="email" value={formData.email} onChange={handleChange} required className={inputClass} />
            {errors.email && <p className="text-red-600 text-xs mt-1">{errors.email}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.password}</label>
            <input type="password" name="password" value={formData.password} onChange={handleChange} required className={inputClass} />
            {errors.password && <p className="text-red-600 text-xs mt-1">{errors.password}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.role}</label>
            <select name="role" value={formData.role} onChange={handleChange} className={inputClass}>
              <option value="patient">{t.patient}</option>
              <option value="doctor">{t.doctor}</option>
            </select>
          </div>
          <button type="submit" className="w-full py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors mt-2">
            {t.signIn}
          </button>
        </form>

        <button onClick={() => navigate("/")} className="w-full mt-3 py-2.5 text-sm font-medium text-slate-500 hover:text-slate-800 transition-colors">
          {t.backToHome}
        </button>

        {message && (
          <p className="mt-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2.5">{message}</p>
        )}
      </div>
    </div>
  );
}

export default Login;
