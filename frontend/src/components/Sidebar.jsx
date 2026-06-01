import React, { useContext } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AuthContext } from '../App';
import toast from 'react-hot-toast';
import { apiFetch } from '../api';

function Sidebar() {
  const { setIsAuthenticated } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async (e) => {
    e.preventDefault();
    try {
      await apiFetch('/api/auth/logout', { method: 'POST' });
      setIsAuthenticated(false);
      navigate('/login');
    } catch (err) {
      toast.error('Failed to log out safely.');
    }
  };

  const navItems = [
    { path: '/', icon: 'bi-grid-1x2', label: 'Overview' },
    { path: '/add-product', icon: 'bi-plus-square', label: 'Add Item' },
    { path: '/upload-data', icon: 'bi-cloud-arrow-up', label: 'Upload Data' },
  ];

  return (
    <div className="d-flex flex-column h-100">
      <div className="mb-5 mt-2 d-flex align-items-center gap-2">
        <div className="bg-white text-black rounded d-flex align-items-center justify-content-center" style={{width:'24px', height:'24px'}}>
          <i className="bi bi-box-seam" style={{fontSize: '0.8rem'}}></i>
        </div>
        <h4 className="mb-0 text-white fw-semibold" style={{ letterSpacing: '-0.5px' }}>
          SupplyBot
        </h4>
      </div>
      
      <ul className="nav flex-column gap-1 position-relative flex-grow-1">
        {navItems.map(item => (
          <li className="nav-item position-relative" key={item.path}>
            <NavLink to={item.path} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} style={{ zIndex: 2 }}>
              <i className={`bi ${item.icon} text-secondary`}></i> 
              <span className="mt-1">{item.label}</span>
            </NavLink>
            {location.pathname === item.path && (
              <motion.div 
                layoutId="sidebar-active-indicator"
                className="position-absolute start-0 top-0 bottom-0 w-100 rounded"
                style={{ background: 'rgba(255,255,255,0.06)', zIndex: 0 }}
                transition={{ type: "tween", ease: "circOut", duration: 0.2 }}
              />
            )}
          </li>
        ))}
      </ul>

      <div className="mt-auto border-top border-secondary border-opacity-25 pt-3">
        <a href="#" className="nav-link text-secondary" onClick={handleLogout}>
          <i className="bi bi-box-arrow-right"></i> 
          <span className="mt-1">Sign Out</span>
        </a>
      </div>
    </div>
  );
}

export default Sidebar;
