import { useState } from 'react';
import { useNavigate } from "react-router-dom";
import { useLanguage } from './LanguageContext';
import { useToast } from './components/ToastContext';

function Register() {
  const { t } = useLanguage();
  const showToast = useToast();
  const [formData, setFormData] = useState({
    full_name: '', username: '', email: '', password: '', role: 'client', specialization: ''
  });
  const [errors, setErrors] = useState({});
  const navigate = useNavigate();

  const specializations = [
    'Cardiologist', 'Dermatologist', 'Neurologist', 'Orthopedist',
    'Pediatrician', 'Ophthalmologist', 'Oncologist', 'Gastroenterologist',
    'Endocrinologist', 'Psychiatrist', 'Urologist', 'Gynecologist',
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const validate = () => {
    const e = {};
    if (!formData.full_name) e.full_name = t.fullNameRequired;
    else if (formData.full_name.length < 2) e.full_name = t.fullNameMin;
    if (!formData.username) e.username = t.usernameRequired;
    if (!formData.email) e.email = t.emailRequired;
    else if (!/\S+@\S+\.\S+/.test(formData.email)) e.email = t.emailInvalid;
    if (!formData.password) e.password = t.passwordRequired;
    else if (formData.password.length < 6) e.password = t.passwordMin;
    else if (!/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/.test(formData.password)) e.password = t.passwordFormat;
    if (formData.role === 'doctor' && !formData.specialization) e.specialization = t.specializationRequired;
    return e;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) { setErrors(newErrors); return; }
    fetch('/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.error) showToast(data.error, 'error');
        else { showToast(data.message, 'success'); navigate("/login"); }
      })
      .catch(() => showToast(t.errorOccurred, 'error'));
  };

  const inputClass = "w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/10 text-slate-800";

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-50 flex items-center justify-center px-6 py-10 font-sans">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <span className="text-2xl font-bold text-blue-700">{t.appName}</span>
        </div>
        <h2 className="text-lg font-semibold text-slate-800 mb-5 text-center">{t.registerTitle}</h2>

        <form onSubmit={handleSubmit} noValidate className="bg-white border border-slate-200 rounded-xl p-7 shadow-sm space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.fullName}</label>
            <input type="text" name="full_name" value={formData.full_name} onChange={handleChange} required className={inputClass} />
            {errors.full_name && <p className="text-red-600 text-xs mt-1">{errors.full_name}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.username}</label>
            <input type="text" name="username" value={formData.username} onChange={handleChange} required className={inputClass} />
            {errors.username && <p className="text-red-600 text-xs mt-1">{errors.username}</p>}
          </div>
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
              <option value="client">{t.client}</option>
              <option value="doctor">{t.doctor}</option>
            </select>
          </div>
          {formData.role === 'doctor' && (
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1.5">{t.specialization}</label>
              <select name="specialization" value={formData.specialization} onChange={handleChange} required className={inputClass}>
                <option value="">{t.selectSpecialization}</option>
                {specializations.map((spec, i) => <option key={i} value={spec}>{spec}</option>)}
              </select>
              {errors.specialization && <p className="text-red-600 text-xs mt-1">{errors.specialization}</p>}
            </div>
          )}
          <button type="submit" className="w-full py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
            {t.register}
          </button>
          <button type="button" onClick={() => navigate("/login")} className="w-full py-2.5 text-sm font-medium text-slate-600 bg-white border border-slate-300 hover:bg-slate-50 rounded-lg transition-colors">
            {t.alreadyHaveAccountSignIn}
          </button>
        </form>

        <button onClick={() => navigate("/")} className="w-full mt-3 py-2.5 text-sm font-medium text-slate-500 hover:text-slate-800 transition-colors">
          {t.backToHome}
        </button>

      </div>
    </div>
  );
}

export default Register;
