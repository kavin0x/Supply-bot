import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { apiFetch } from '../api';

function ProductCard({ product, onUpdateInventory }) {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [qty, setQty] = useState('');
  const [type, setType] = useState('in');

  const predictDemand = async () => {
    setLoading(true);
    const toastId = toast.loading('Analyzing inventory patterns...');
    try {
      const res = await apiFetch(`/api/ai/predict/${product.id}`);
      const data = await res.json();
      if (data.error) {
        toast.error(data.error, { id: toastId });
      } else {
        setPrediction(data.prediction);
        toast.success('Analysis complete', { id: toastId });
      }
    } catch (err) {
      toast.error('Failed to communicate with AI service.', { id: toastId });
    }
    setLoading(false);
  };

  const handleUpdate = (e) => {
    e.preventDefault();
    if (!qty || isNaN(qty) || qty <= 0) return toast.error('Enter a valid quantity');
    onUpdateInventory(product.id, qty, type);
    setQty('');
  };

  return (
    <div className="surface h-100 d-flex flex-column">
      <div className="p-4 pb-0 d-flex justify-content-between align-items-start">
        <div>
          <h5 className="text-white fw-semibold mb-1">{product.name}</h5>
          <span className="text-muted small px-2 py-1 rounded bg-white bg-opacity-10 border border-white border-opacity-10">
            {product.category}
          </span>
        </div>
        <h4 className="mb-0 text-white fw-semibold">${Number(product.price).toFixed(2)}</h4>
      </div>
      
      <div className="p-4 d-flex flex-column flex-grow-1">
        <p className="text-secondary small mb-4 flex-grow-1">{product.description}</p>
        
        <div className="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom border-secondary border-opacity-25">
          <span className="text-muted small text-uppercase fw-semibold" style={{letterSpacing: '0.5px'}}>Current Stock</span>
          <span className="text-white fw-bold fs-5">{product.quantity}</span>
        </div>
        
        <div className="mb-4">
          <button className="btn btn-secondary w-100" onClick={predictDemand} disabled={loading}>
            {loading ? <span className="spinner-border spinner-border-sm me-2" /> : <i className="bi bi-stars me-2"></i>} 
            AI Analysis
          </button>
        </div>
        
        <AnimatePresence>
          {prediction && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-4 overflow-hidden"
              transition={{ duration: 0.2 }}
            >
              <div className="ai-report">
                <div className="d-flex align-items-center gap-2 mb-3 pb-2 border-bottom border-secondary border-opacity-25">
                  <i className="bi bi-robot text-secondary"></i>
                  <span className="text-white fw-semibold" style={{fontSize: '0.85rem'}}>AI Insight</span>
                </div>
                <div dangerouslySetInnerHTML={{ __html: prediction.replace(/\n/g, '<br>') }}></div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        
        <form className="d-flex gap-2 align-items-center mt-auto" onSubmit={handleUpdate}>
          <input type="number" className="form-control form-control-sm" value={qty} onChange={e => setQty(e.target.value)} placeholder="Qty" required />
          <select className="form-select form-select-sm" style={{width: '90px'}} value={type} onChange={e => setType(e.target.value)} required>
            <option value="in">Add</option>
            <option value="out">Remove</option>
          </select>
          <button type="submit" className="btn btn-outline-secondary btn-sm" title="Update Stock">
            <i className="bi bi-check-lg"></i>
          </button>
        </form>
      </div>
    </div>
  );
}

export default ProductCard;
