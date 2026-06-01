import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import { apiFetch } from './api';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import AddProduct from './pages/AddProduct';
import UploadData from './pages/UploadData';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Report from './pages/Report';

export const AuthContext = React.createContext();

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch('/api/auth/status')
      .then(res => res.json())
      .then(data => {
        setIsAuthenticated(data.authenticated);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="d-flex justify-content-center align-items-center vh-100 bg-black">
      <div className="spinner-border text-light" role="status">
        <span className="visually-hidden">Loading...</span>
      </div>
    </div>
  );

  return (
    <AuthContext.Provider value={{ isAuthenticated, setIsAuthenticated }}>
      <Router>
        <Toaster 
          position="top-right" 
          toastOptions={{
            style: {
              background: '#111',
              color: '#fff',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '6px'
            }
          }}
        />
        <AppContent />
      </Router>
    </AuthContext.Provider>
  );
}

function AppContent() {
  const { isAuthenticated } = React.useContext(AuthContext);
  const location = useLocation();
  const isAuthRoute = location.pathname === '/login' || location.pathname === '/signup';

  if (!isAuthenticated && !isAuthRoute) {
    return <Navigate to="/login" replace />;
  }

  if (isAuthenticated && isAuthRoute) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="container-fluid p-0">
      <div className="row g-0">
        {isAuthenticated && (
          <div className="col-md-3 col-lg-2 sidebar">
            <Sidebar />
          </div>
        )}
        <div className={isAuthenticated ? "col-md-9 col-lg-10 main-content position-relative" : "col-12 position-relative"}>
          <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/" element={<Dashboard />} />
              <Route path="/add-product" element={<AddProduct />} />
              <Route path="/upload-data" element={<UploadData />} />
              <Route path="/report" element={<Report />} />
            </Routes>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

export default App;
