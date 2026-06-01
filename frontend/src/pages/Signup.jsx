import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AuthContext } from '../App';
import toast from 'react-hot-toast';
import { apiFetch } from '../api';

function Signup() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { setIsAuthenticated } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!username || !password || !confirmPassword) {
      toast.error('Please fill in all fields');
      return;
    }

    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    setLoading(true);
    const toastId = toast.loading('Creating account...');

    try {
      const res = await apiFetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await res.json();

      if (res.ok && data.success) {
        toast.success('Account created', { id: toastId });
        setIsAuthenticated(true);
        navigate('/');
      } else {
        toast.error(data.error || 'Signup failed', { id: toastId });
      }
    } catch (err) {
      toast.error('Network error', { id: toastId });
    }

    setLoading(false);
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      className="container"
      style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
    >
      <div className="row justify-content-center w-100">
        <div className="col-md-6 col-lg-4">
          <div className="text-center mb-5">
            <div className="bg-white text-black rounded d-inline-flex align-items-center justify-content-center mb-3" style={{width:'40px', height:'40px'}}>
              <i className="bi bi-box-seam fs-4"></i>
            </div>
            <h2 className="fw-semibold text-white mb-1" style={{ letterSpacing: '-0.5px' }}>
              SupplyBot
            </h2>
            <p className="text-secondary small">Create your account</p>
          </div>

          <div className="surface p-5">
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="form-label text-secondary small fw-medium">Username</label>
                <input type="text" className="form-control" value={username} onChange={e => setUsername(e.target.value)} required />
              </div>

              <div className="mb-4">
                <label className="form-label text-secondary small fw-medium">Password</label>
                <input type="password" className="form-control" value={password} onChange={e => setPassword(e.target.value)} required />
              </div>

              <div className="mb-5">
                <label className="form-label text-secondary small fw-medium">Confirm Password</label>
                <input type="password" className="form-control" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} required />
              </div>

              <div className="d-grid">
                <button type="submit" className="btn btn-primary w-100" disabled={loading}>
                  {loading ? <span className="spinner-border spinner-border-sm" /> : 'Create Account'}
                </button>
              </div>

              <div className="text-center mt-3">
                <span className="text-secondary small">Already have an account? </span>
                <Link to="/login" className="small text-decoration-none">
                  Sign in
                </Link>
              </div>
            </form>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export default Signup;