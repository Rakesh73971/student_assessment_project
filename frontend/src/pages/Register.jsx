import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/useAuth';
import { formatApiErrorDetail } from '../utils/formatApiError';
import { getDefaultRouteForRole } from '../utils/auth';
import { UserPlus, AlertCircle } from 'lucide-react';
import './Register.css';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    role: 'student'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const user = await register(formData);
      navigate(getDefaultRouteForRole(user?.role));
    } catch (err) {
      const detail = formatApiErrorDetail(err.response?.data?.detail);
      setError(detail || err.friendlyMessage || 'Failed to register. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-page flex-center animate-fade-in">
      <div className="register-card glass-panel">
        <div className="register-header">
          <h2 className="register-title">Create an Account</h2>
          <p>Join AssessAI today</p>
        </div>

        {error && (
          <div className="register-error flex-center">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="full_name">Full Name</label>
            <input 
              type="text" 
              id="full_name"
              name="full_name"
              className="form-input" 
              placeholder="John Doe" 
              value={formData.full_name}
              onChange={handleChange}
            />
          </div>
          
          <div className="form-group">
            <label className="form-label" htmlFor="email">Email Address</label>
            <input 
              type="email" 
              id="email"
              name="email"
              className="form-input" 
              placeholder="you@example.com" 
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <input 
              type="password" 
              id="password"
              name="password"
              className="form-input" 
              placeholder="Min. 8 characters" 
              value={formData.password}
              onChange={handleChange}
              required
              minLength="8"
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">I am a...</label>
            <div className="register-role-options">
              <label className={`register-role-option ${formData.role === 'student' ? 'is-selected' : ''}`}>
                <input type="radio" name="role" value="student" checked={formData.role === 'student'} onChange={handleChange} className="register-role-input" />
                <span className="register-role-label">Student</span>
              </label>
              <label className={`register-role-option ${formData.role === 'instructor' ? 'is-selected' : ''}`}>
                <input type="radio" name="role" value="instructor" checked={formData.role === 'instructor'} onChange={handleChange} className="register-role-input" />
                <span className="register-role-label">Instructor</span>
              </label>
            </div>
          </div>
          
          <button 
            type="submit" 
            className="register-submit btn btn-primary" 
            disabled={loading}
          >
            {loading ? 'Creating account...' : (
              <>
                <UserPlus size={18} />
                <span>Create Account</span>
              </>
            )}
          </button>
        </form>
        
        <div className="register-footer">
          Already have an account? <Link to="/login" className="register-link">Sign in</Link>
        </div>
      </div>
    </div>
  );
};

export default Register;
