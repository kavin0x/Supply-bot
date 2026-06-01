from typing import Dict, Any, Tuple, Optional, List
from backend.ai.features.client import client, MODEL_NAME, AGENT_SYSTEM_PROMPT

async def predict_demand(product_data: Dict[str, Any], transactions: List[Dict[str, Any]]) -> Tuple[Optional[str], Optional[str]]:
    try:
        # Create context from transactions
        history_context = "\n".join([f"- {t.get('date', 'Unknown')}: {t.get('transaction_type', 'Unknown')} {t.get('quantity', 0)} units" for t in transactions])
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": f"""Analyze this product's inventory:
                Name: {product_data.get('name', 'N/A')}
                Category: {product_data.get('category', 'N/A')}
                Current Stock: {product_data.get('quantity', 0)}
                Price: ${product_data.get('price', 0)}
                
                Recent Transaction History:
                {history_context if history_context else 'No recent transactions.'}
                
                Provide:
                1. Demand prediction for the next week
                2. Optimal stock level recommendations
                3. Risk assessment for stockouts or overstock
                4. Actionable recommendations based on the actual history provided above."""}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content, None
    except Exception as e:
        return None, str(e)
