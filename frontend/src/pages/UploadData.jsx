import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { apiFetch } from '../api';

const pageVariants = {
  initial: { opacity: 0 },
  in: { opacity: 1 },
  out: { opacity: 0 }
};

function UploadData() {
  const [file, setFile] = useState(null);
  const [dataType, setDataType] = useState('transactions');
  const [dateFormat, setDateFormat] = useState('%Y-%m-%d');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return toast.error('Please select a file to upload');
    
    setLoading(true);
    const toastId = toast.loading('Uploading and processing data...');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('data_type', dataType);
    formData.append('date_format', dateFormat);

    try {
      const res = await apiFetch('/api/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        toast.success(data.message || 'Data uploaded successfully', { id: toastId });
        navigate('/');
      } else {
        toast.error(data.error || 'Upload failed', { id: toastId });
      }
    } catch (err) {
      toast.error('Network error during upload', { id: toastId });
    }
    setLoading(false);
  };

  return (
    <motion.div initial="initial" animate="in" exit="out" variants={pageVariants} transition={{ duration: 0.2 }} className="row justify-content-center">
      <div className="col-md-8 col-lg-6">
        <div className="mb-4 pb-3 border-bottom border-secondary border-opacity-25">
          <h2 className="mb-1 text-white fw-semibold">Upload Data</h2>
          <p className="text-secondary mb-0">Import spreadsheets to expand the AI context window.</p>
        </div>

        <div className="surface p-4 p-md-5">
          <form onSubmit={handleSubmit}>
            
            <div className="mb-4 text-center p-5 rounded" id="drop-area">
              <i className="bi bi-cloud-arrow-up display-4 text-secondary mb-3"></i>
              <h6 className="text-white fw-semibold">Select a file</h6>
              <p className="text-secondary small">CSV, XLSX, or JSON (Max: 16MB)</p>
              <input className="form-control mt-3 form-control-sm" type="file" onChange={handleFileChange} required accept=".csv, .xlsx, .xls, .json" />
            </div>

            <div className="row mb-4">
              <div className="col-md-6">
                <label className="form-label text-secondary small fw-medium">Data Type</label>
                <select className="form-select" value={dataType} onChange={e => setDataType(e.target.value)} required>
                  <option value="transactions">Transactions</option>
                  <option value="products">Products</option>
                  <option value="sales">Sales</option>
                </select>
              </div>
              <div className="col-md-6 mt-4 mt-md-0">
                <label className="form-label text-secondary small fw-medium">Date Format</label>
                <input type="text" className="form-control" value={dateFormat} onChange={e => setDateFormat(e.target.value)} placeholder="e.g., %Y-%m-%d" />
              </div>
            </div>

            <div className="d-flex justify-content-end pt-4 border-top border-secondary border-opacity-25 mt-4">
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? <span className="spinner-border spinner-border-sm me-2" /> : <i className="bi bi-upload me-2"></i>}
                Upload File
              </button>
            </div>
          </form>
        </div>
      </div>
    </motion.div>
  );
}

export default UploadData;
