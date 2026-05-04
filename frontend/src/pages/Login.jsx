import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/useAuth';
import { formatApiErrorDetail } from '../utils/formatApiError';
import { getDefaultRouteForRole } from '../utils/auth';
import { LogIn, AlertCircle } from 'lucide-react';
import './Login.css';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const user = await login(email, password);
      navigate(getDefaultRouteForRole(user?.role));
    } catch (err) {
      setError(
        formatApiErrorDetail(err?.response?.data?.detail) ||
        err?.friendlyMessage ||
        err?.message ||
        'Login failed. Please check your credentials.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page flex-center animate-fade-in">
      <div className="login-card glass-panel">
        <div className="login-header">
          <h2>Welcome Back</h2>
          <p>Enter your credentials to access your account</p>
        </div>

        {error && (
          <div className="login-error flex-center">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              className="form-input"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="login-submit btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Signing in...' : (
              <>
                <LogIn size={18} />
                <span>Sign In</span>
              </>
            )}
          </button>

        </form>

        <div className="login-footer">
          Don't have an account?{' '}
          <Link to="/register" className="login-link">
            Sign up
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
