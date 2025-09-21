import { useNavigate } from 'react-router-dom';
import './manageAppointment.css';  

function ManageAppointment() {
  const navigate = useNavigate();

  const handleCreateAppointment = () => {
    navigate('/AddAppointment');
  };

  const handleShowAppointment = () => {
    navigate('/ShowAppointment');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    navigate('/login');
  };

  const handleAccount = () => {
    navigate('/account');
  };

  return (
    <div className="manage-container">
      <h2 className="manage-title">Manage Appointments</h2>
      <button className="manage-button manage-add-appointment-button" onClick={handleCreateAppointment}>
        Add Appointment
      </button>
      <button className="manage-button manage-show-appointment-button" onClick={handleShowAppointment}>
        Show Appointment
      </button>
      <button className="manage-button manage-account-button" onClick={handleAccount}>
        Account
      </button>
      <button className="manage-button manage-logout-button" onClick={handleLogout}>
        Logout
      </button>
    </div>
  );
}

export default ManageAppointment;
