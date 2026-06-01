from typing import Tuple, Optional, List, Dict, Any
from backend.ai.features.client import client, MODEL_NAME, AGENT_SYSTEM_PROMPT

async def generate_inventory_report(products: List[Dict[str, Any]], recent_transactions: List[Dict[str, Any]]) -> Tuple[Optional[str], Optional[str]]:
    try:
        # Prepare context
        low_stock = [p for p in products if p.get('quantity', 0) < 10]
        overstock = [p for p in products if p.get('quantity', 0) > 100]
        
        low_stock_ctx = "\n".join([f"- {p.get('name')} (Stock: {p.get('quantity')})" for p in low_stock])
        overstock_ctx = "\n".join([f"- {p.get('name')} (Stock: {p.get('quantity')})" for p in overstock])
        
        tx_ctx = "\n".join([f"- Product ID {t.get('product_id')}: {t.get('transaction_type')} {t.get('quantity')} units on {t.get('date')}" for t in recent_transactions[:20]]) # Top 20 recent
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": f"""Generate a comprehensive inventory report based on the following data:
                
                Total Products: {len(products)}
                Low Stock Items (<10): 
                {low_stock_ctx if low_stock_ctx else 'None'}
                
                Overstocked Items (>100):
                {overstock_ctx if overstock_ctx else 'None'}
                
                Recent Transactions:
                {tx_ctx if tx_ctx else 'None'}
                
                Include:
                1. Overall inventory health
                2. Products at risk of stockout
                3. Overstocked items
                4. Demand trends (based on recent transactions)
                5. Recommendations for optimization"""}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        return response.choices[0].message.content, None
    except Exception as e:
        return None, str(e)
