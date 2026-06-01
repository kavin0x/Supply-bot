# AI features package
from .demand_prediction import predict_demand
from .embeddings import CloudEmbeddingModel, HashEmbeddingModel, cosine_similarity, embedding_payload, text_from_fields
from .inventory_search import search_inventory
from .report_generation import generate_inventory_report
from .data_ingestion import process_data, fine_tune_model

__all__ = [
    'predict_demand',
    'CloudEmbeddingModel',
    'HashEmbeddingModel',
    'cosine_similarity',
    'embedding_payload',
    'text_from_fields',
    'search_inventory',
    'generate_inventory_report',
    'process_data',
    'fine_tune_model'
]
