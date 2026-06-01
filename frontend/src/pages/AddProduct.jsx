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

function AddProduct() {
  const [formData, setFormData] = useState({ name: '', category: '', quantity: 0, price: '', description: '' });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const toastId = toast.loading('Adding product...');
    
    try {
      const res = await apiFetch('/api/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (res.ok) {
        toast.success('Product added', { id: toastId });
        navigate('/');
      } else {
        const data = await res.json();
        toast.error(data.error || 'Failed to add product', { id: toastId });
      }
    } catch (err) {
      toast.error('Network error', { id: toastId });
    }
    setLoading(false);
  };

  return (
    <motion.div initial="initial" animate="in" exit="out" variants={pageVariants} transition={{ duration: 0.2 }} className="row justify-content-center">
      <div className="col-md-8 col-lg-6">
        <div className="mb-4 pb-3 border-bottom border-secondary border-opacity-25">
          <h2 className="mb-1 text-white fw-semibold">Add New Product</h2>
          <p className="text-secondary mb-0">Register a new item into the inventory system.</p>
        </div>

        <div className="surface p-4 p-md-5">
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="form-label text-secondary small fw-medium">Product Name</label>
              <input type="text" className="form-control" name="name" value={formData.name} onChange={handleChange} required placeholder="e.g. Premium Widget" />
            </div>
            
            <div className="mb-4">
              <label className="form-label text-secondary small fw-medium">Category</label>
              <input type="text" className="form-control" name="category" value={formData.category} onChange={handleChange} required placeholder="e.g. Electronics" />
            </div>

            <div className="row mb-4">
              <div className="col-md-6">
                <label className="form-label text-secondary small fw-medium">Initial Stock</label>
                <input type="number" className="form-control" name="quantity" value={formData.quantity} onChange={handleChange} required min="0" />
              </div>
              <div className="col-md-6 mt-4 mt-md-0">
                <label className="form-label text-secondary small fw-medium">Unit Price ($)</label>
                <div className="input-group">
                  <span className="input-group-text border-end-0">$</span>
                  <input type="number" step="0.01" className="form-control border-start-0 ps-0" name="price" value={formData.price} onChange={handleChange} required min="0" placeholder="0.00" />
                </div>
              </div>
            </div>

            <div className="mb-5">
              <label className="form-label text-secondary small fw-medium">Description</label>
              <textarea className="form-control" name="description" rows="3" value={formData.description} onChange={handleChange} placeholder="Optional details..."></textarea>
            </div>

            <div className="d-flex justify-content-end gap-2 pt-4 border-top border-secondary border-opacity-25">
              <button type="button" onClick={() => navigate('/')} className="btn btn-outline-secondary">Cancel</button>
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? <span className="spinner-border spinner-border-sm me-2" /> : null}
                Save Product
              </button>
            </div>
          </form>
        </div>
      </div>
    </motion.div>
  );
}

export default AddProduct;
