from typing import Tuple, Optional, List, Dict, Any

from backend.ai.features.client import client, MODEL_NAME
from backend.ai.features.embeddings import HashEmbeddingModel, cosine_similarity, text_from_fields

EMBEDDING_MODEL = HashEmbeddingModel()


def _product_search_text(product: Dict[str, Any]) -> str:
    return text_from_fields(
        product.get('name'),
        product.get('description'),
        product.get('category'),
        product.get('quantity'),
        product.get('price'),
    )

async def search_inventory(
    query: str,
    all_products: List[Dict[str, Any]],
    stored_embeddings: Optional[Dict[int, List[float]]] = None,
) -> Tuple[Optional[str], Optional[str]]:
    try:
        if not all_products:
            return None, 'No products available to search.'

        query_vector = EMBEDDING_MODEL.embed(query)
        ranked_products = []

        for product in all_products:
            product_text = _product_search_text(product)
            if not product_text:
                continue

            product_id = product.get('id')
            product_vector = None
            if stored_embeddings and product_id in stored_embeddings:
                product_vector = stored_embeddings[product_id]

            if product_vector is not None:
                try:
                    score = cosine_similarity(query_vector, product_vector)
                except ValueError:
                    product_vector = None

            if product_vector is None:
                product_vector = EMBEDDING_MODEL.embed(product_text)

            score = cosine_similarity(query_vector, product_vector)
            ranked_products.append((score, product))

        ranked_products.sort(key=lambda item: item[0], reverse=True)
        top_matches = ranked_products[:5]

        if not top_matches:
            return None, 'No searchable product text was available.'

        products_context = "\n".join(
            [
                f"- Score: {score:.3f} | ID: {product.get('id')}, Name: {product.get('name')}, Stock: {product.get('quantity')}, Price: ${product.get('price')}, Category: {product.get('category', 'N/A')}, Description: {product.get('description', 'N/A')}"
                for score, product in top_matches
            ]
        )
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an AI inventory search assistant with deep knowledge of inventory management. Use the ranked product matches provided below to answer the user's search query. Focus on the best matches rather than summarizing the entire catalog."},
                {"role": "user", "content": f"""Search the inventory with this query: {query}
                
                Ranked Inventory Matches:
                {products_context}
                
                Provide:
                1. Relevant products matching the search
                2. Current stock levels of those products
                3. Any relevant insights or recommendations"""}
            ],
            temperature=0.5,
            max_tokens=800
        )
        return response.choices[0].message.content, None
    except Exception as e:
        return None, str(e)
