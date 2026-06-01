import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import ProductCard from '../components/ProductCard';
import { apiFetch } from '../api';

const pageVariants = {
  initial: { opacity: 0 },
  in: { opacity: 1 },
  out: { opacity: 0 }
};

function Dashboard() {
  const [products, setProducts] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResult, setSearchResult] = useState(null);
  const [searching, setSearching] = useState(false);
  const navigate = useNavigate();

  const fetchProducts = async () => {
    try {
      const res = await apiFetch('/api/products');
      if (res.ok) {
        const data = await res.json();
        setProducts(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleUpdateInventory = async (productId, quantity, type) => {
    const toastId = toast.loading('Updating inventory...');
    try {
      const res = await apiFetch(`/api/inventory/${productId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity, type })
      });
      if (res.ok) {
        await fetchProducts();
        toast.success('Inventory updated', { id: toastId });
      } else {
        const data = await res.json();
        toast.error(data.error || 'Failed to update', { id: toastId });
      }
    } catch (err) {
      toast.error('Network error', { id: toastId });
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery) return;
    setSearching(true);
    const toastId = toast.loading('Analyzing inventory...');
    try {
      const res = await apiFetch('/api/ai/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery })
      });
      const data = await res.json();
      if (data.error) {
        toast.error(data.error, { id: toastId });
      } else {
        setSearchResult(data.result);
        toast.success('Analysis complete', { id: toastId });
      }
    } catch (err) {
      toast.error('Search failed', { id: toastId });
    }
    setSearching(false);
  };

  const injectContext = async () => {
    const toastId = toast.loading('Synchronizing AI context...');
    try {
      const res = await apiFetch('/api/ai/inject-context', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        toast.success(data.message || 'Context synchronized', { id: toastId });
      } else {
        toast.error(data.error || 'Synchronization failed', { id: toastId });
      }
    } catch (err) {
      toast.error('Network error', { id: toastId });
    }
  };

  return (
    <motion.div 
      initial="initial" animate="in" exit="out" variants={pageVariants} transition={{ duration: 0.2 }}
    >
      <div className="d-flex justify-content-between align-items-center mb-5 pb-3 border-bottom border-secondary border-opacity-25">
        <div>
          <h2 className="mb-1 text-white fw-semibold">Inventory Overview</h2>
          <p className="text-secondary mb-0">Manage stock, predict demand, and generate insights.</p>
        </div>
        
        <div className="d-flex gap-3">
          <button onClick={injectContext} className="btn btn-outline-secondary">
            <i className="bi bi-arrow-repeat"></i> Sync AI Context
          </button>
          <button onClick={() => navigate('/report')} className="btn btn-primary">
            <i className="bi bi-file-earmark-text"></i> Generate Report
          </button>
        </div>
      </div>

      <div className="row mb-5">
        <div className="col-12">
          <div className="surface p-2 d-flex align-items-center">
            <i className="bi bi-search text-secondary ms-3 me-2"></i>
            <form onSubmit={handleSearch} className="flex-grow-1 m-0">
              <input type="text" className="form-control border-0 shadow-none bg-transparent" 
                     value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
                placeholder="Search inventory by meaning... (e.g. 'show me low stock items')" 
                     disabled={searching} />
              <button type="submit" className="d-none">Search</button>
            </form>
          </div>
        </div>
      </div>
      
      <AnimatePresence>
        {searchResult && (
          <motion.div initial={{opacity:0, y:-10}} animate={{opacity:1, y:0}} exit={{opacity:0, height:0}} className="ai-report mb-5 position-relative">
            <button className="btn-close btn-close-white position-absolute top-0 end-0 m-3" onClick={() => setSearchResult(null)} style={{filter: 'invert(1)'}}></button>
            <h6 className="text-white mb-3 fw-semibold"><i className="bi bi-stars text-secondary me-2"></i>AI Analysis Results</h6>
            <div dangerouslySetInnerHTML={{ __html: searchResult.replace(/\n/g, '<br>') }}></div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="row g-4">
        {products.map(product => (
          <div className="col-md-6 col-xl-4" key={product.id}>
            <ProductCard product={product} onUpdateInventory={handleUpdateInventory} />
          </div>
        ))}
        {products.length === 0 && (
          <div className="col-12 text-center py-5 my-5">
            <div className="d-inline-block text-center">
              <i className="bi bi-inboxes text-muted display-4 mb-3"></i>
              <h5 className="text-white fw-semibold">No items found</h5>
              <p className="text-secondary mb-4">Get started by adding products to your inventory.</p>
              <button onClick={() => navigate('/add-product')} className="btn btn-primary">
                <i className="bi bi-plus-lg"></i> Add Product
              </button>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}

export default Dashboard;
