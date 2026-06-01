import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { apiFetch } from '../api';

const pageVariants = {
  initial: { opacity: 0 },
  in: { opacity: 1 },
  out: { opacity: 0 }
};

function Report() {
  const [report, setReport] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const res = await apiFetch('/api/ai/report');
        const data = await res.json();
        if (data.error) {
          toast.error(data.error);
        } else {
          setReport(data.report);
        }
      } catch (err) {
        toast.error('Failed to generate report');
      }
      setLoading(false);
    };
    fetchReport();
  }, []);

  return (
    <motion.div initial="initial" animate="in" exit="out" variants={pageVariants} transition={{ duration: 0.2 }} className="row justify-content-center">
      <div className="col-lg-10">
        <div className="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom border-secondary border-opacity-25">
          <div>
            <h2 className="mb-1 text-white fw-semibold">AI Analysis Report</h2>
            <p className="text-secondary mb-0">Comprehensive system diagnostics.</p>
          </div>
          <button onClick={() => navigate('/')} className="btn btn-outline-secondary">
            <i className="bi bi-arrow-left me-2"></i>Back to Dashboard
          </button>
        </div>

        <div className="surface mb-5">
          <div className="p-4 p-md-5">
            {loading ? (
              <div className="text-center py-5 my-5">
                <div className="spinner-border text-secondary" role="status"></div>
                <p className="text-secondary mt-3 fw-medium">Generating comprehensive AI report...</p>
              </div>
            ) : (
              <motion.div initial={{opacity:0}} animate={{opacity:1}} className="ai-report" style={{ whiteSpace: 'pre-wrap' }}>
                {report}
              </motion.div>
            )}
          </div>
        </div>
        
        {!loading && (
          <motion.div initial={{opacity:0, y:10}} animate={{opacity:1, y:0}} className="text-center mb-5">
            <button className="btn btn-primary px-4" onClick={() => window.print()}>
              <i className="bi bi-printer me-2"></i> Print Report
            </button>
          </motion.div>
        )}
      </div>

      <style>{`
        @media print {
          body { background: white; color: black; }
          .sidebar, .btn { display: none !important; }
          .surface { box-shadow: none !important; border: none !important; }
          .text-white, .text-secondary { color: black !important; }
          .ai-report { background: none !important; border: 1px solid #e4e4e7 !important; color: black !important; }
        }
      `}</style>
    </motion.div>
  );
}

export default Report;
