import os
import json
import openai
from datetime import datetime
from dotenv import load_dotenv
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional, Tuple, Union
import pandas as pd
import tempfile
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

load_dotenv()
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class DataType(Enum):
    TRANSACTIONS = "transactions"
    PRODUCTS = "products"
    SALES = "sales"

@dataclass
class ProcessingResult:
    success: bool
    message: str
    data: Optional[List[Dict[str, str]]] = None
    file_path: Optional[str] = None

class GPTInventoryModel:
    def __init__(self, model_name: str = "gpt-4o-mini", training_data_dir: str = "training_data"):
        """Initialize the GPT Inventory Model with a specified model name.
        
        Args:
            model_name: The OpenAI model to use (default: gpt-4o-mini)
            training_data_dir: Directory to store training data files
        """
        self.model_name = model_name
        self.fine_tuned_model = None
        self.training_data = []
        self.training_data_dir = training_data_dir
        os.makedirs(training_data_dir, exist_ok=True)
        
        self.agent_system_prompt = """You are an AI inventory management agent with the following capabilities:
        1. Analyze inventory patterns and predict demand
        2. Suggest optimal stock levels based on historical data
        3. Identify potential stockouts and overstock situations
        4. Provide recommendations for inventory optimization
        5. Generate detailed reports on inventory performance"""
    
    def process_data(self, file_path: str, data_type: Union[str, DataType], date_format: str = "%Y-%m-%d") -> ProcessingResult:
        """Process uploaded data and convert it to JSONL format.
        
        Args:
            file_path: Path to the data file
            data_type: Type of data (transactions, products, or sales)
            date_format: Format of dates in the file
            
        Returns:
            ProcessingResult containing success status, message, and processed data
        """
        try:
            if isinstance(data_type, str):
                data_type = DataType(data_type.lower())
            
            # Read the file based on its extension
            file_ext = Path(file_path).suffix.lower()
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif file_ext == '.json':
                df = pd.read_json(file_path)
            else:
                return ProcessingResult(False, "Unsupported file format. Please use CSV, Excel, or JSON files.")
            
            # Process data based on type
            if data_type == DataType.TRANSACTIONS:
                training_data = self._process_transaction_data(df, date_format)
            elif data_type == DataType.PRODUCTS:
                training_data = self._process_product_data(df)
            elif data_type == DataType.SALES:
                training_data = self._process_sales_data(df, date_format)
            else:
                return ProcessingResult(False, f"Invalid data type: {data_type}")
            
            # Save to JSONL file in training data directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            jsonl_filename = f"{data_type.value}_{timestamp}.jsonl"
            jsonl_path = os.path.join(self.training_data_dir, jsonl_filename)
            
            self._save_to_jsonl(training_data, jsonl_path)
            
            return ProcessingResult(
                success=True,
                message="Data processed successfully",
                data=training_data,
                file_path=jsonl_path
            )
            
        except Exception as e:
            return ProcessingResult(False, f"Error processing data: {str(e)}")
    
    def _process_transaction_data(self, df: pd.DataFrame, date_format: str) -> List[Dict[str, str]]:
        """Process transaction data into training examples."""
        training_examples = []
        
        try:
            # Convert date column to datetime
            df['date'] = pd.to_datetime(df['date'], format=date_format)
            
            for _, row in df.iterrows():
                prompt = self._create_transaction_prompt(row)
                completion = self._generate_completion_from_data(row)
                training_examples.append({
                    "prompt": prompt,
                    "completion": completion
                })
            
            return training_examples
        except Exception as e:
            raise Exception(f"Error processing transaction data: {str(e)}")
    
    def _create_transaction_prompt(self, row: pd.Series) -> str:
        """Create a prompt for transaction data analysis."""
        return f"""Transaction Data:
Date: {row['date'].strftime('%Y-%m-%d')}
Product ID: {row.get('product_id', 'N/A')}
Product Name: {row.get('product_name', 'N/A')}
Transaction Type: {row.get('transaction_type', 'N/A')}
Quantity: {row.get('quantity', 0)}
Price: {row.get('price', 0)}
Category: {row.get('category', 'N/A')}

Analyze this transaction and predict future demand patterns:"""
    
    def _process_product_data(self, df: pd.DataFrame) -> List[Dict[str, str]]:
        """Process product catalog data into training examples."""
        training_examples = []
        
        try:
            for _, row in df.iterrows():
                prompt = self._create_product_prompt(row)
                completion = self._generate_completion_from_data(row)
                training_examples.append({
                    "prompt": prompt,
                    "completion": completion
                })
            
            return training_examples
        except Exception as e:
            raise Exception(f"Error processing product data: {str(e)}")
    
    def _create_product_prompt(self, row: pd.Series) -> str:
        """Create a prompt for product data analysis."""
        return f"""Product Information:
Name: {row.get('name', 'N/A')}
Category: {row.get('category', 'N/A')}
Description: {row.get('description', 'N/A')}
Current Stock: {row.get('quantity', 0)}
Price: ${row.get('price', 0)}
Last Updated: {row.get('last_updated', 'N/A')}

Analyze this product's inventory status and predict optimal stock levels:"""
    
    def _process_sales_data(self, df: pd.DataFrame, date_format: str) -> List[Dict[str, str]]:
        """Process sales data into training examples."""
        training_examples = []
        
        try:
            df['date'] = pd.to_datetime(df['date'], format=date_format)
            
            for _, row in df.iterrows():
                prompt = self._create_sales_prompt(row)
                completion = self._generate_completion_from_data(row)
                training_examples.append({
                    "prompt": prompt,
                    "completion": completion
                })
            
            return training_examples
        except Exception as e:
            raise Exception(f"Error processing sales data: {str(e)}")
    
    def _create_sales_prompt(self, row: pd.Series) -> str:
        """Create a prompt for sales data analysis."""
        return f"""Sales Data:
Date: {row['date'].strftime('%Y-%m-%d')}
Product ID: {row.get('product_id', 'N/A')}
Product Name: {row.get('product_name', 'N/A')}
Quantity Sold: {row.get('quantity', 0)}
Revenue: ${row.get('revenue', 0)}
Customer Segment: {row.get('customer_segment', 'N/A')}

Analyze this sales data and predict future sales patterns:"""
    
    def _generate_completion_from_data(self, row: pd.Series) -> str:
        """Generate completion text using GPT for the given data row."""
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.agent_system_prompt},
                    {"role": "user", "content": f"Analyze this data and provide insights: {row.to_dict()}"}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating completion: {str(e)}"
    
    def _save_to_jsonl(self, training_data: List[Dict[str, str]], file_path: str) -> None:
        """Save training data to a JSONL file."""
        with open(file_path, 'w') as f:
            for example in training_data:
                f.write(json.dumps(example) + '\n')
    
    def fine_tune_model(self, jsonl_path: str) -> Tuple[bool, str]:
        """Fine-tune the model using the prepared JSONL file."""
        try:
            # Upload the training file
            with open(jsonl_path, 'rb') as f:
                response = client.files.create(
                    file=f,
                    purpose='fine-tune'
                )
            file_id = response.id
            
            # Start the fine-tuning job
            fine_tune_response = client.fine_tuning.jobs.create(
                training_file=file_id,
                model=self.model_name,
                hyperparameters={
                    "n_epochs": 3,
                    "batch_size": 4,
                    "learning_rate_multiplier": 0.1
                }
            )
            
            self.fine_tuned_model = fine_tune_response.id
            return True, "Fine-tuning started successfully"
        except Exception as e:
            return False, str(e)
    
    async def predict_demand(self, product_data: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
        """Use the fine-tuned model to predict demand with enhanced analysis."""
        if not self.fine_tuned_model:
            return None, "Model not fine-tuned yet"
        
        try:
            response = await client.chat.completions.create(
                model=self.fine_tuned_model,
                messages=[
                    {"role": "system", "content": self.agent_system_prompt},
                    {"role": "user", "content": f"""Analyze this product's inventory:
                    Name: {product_data['name']}
                    Category: {product_data['category']}
                    Current Stock: {product_data['quantity']}
                    Price: ${product_data['price']}
                    
                    Provide:
                    1. Demand prediction for the next week
                    2. Optimal stock level recommendations
                    3. Risk assessment for stockouts or overstock
                    4. Actionable recommendations"""}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content, None
        except Exception as e:
            return None, str(e)
    
    def search_inventory(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """Use the model for intelligent inventory search."""
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an AI inventory search assistant with deep knowledge of inventory management."},
                    {"role": "user", "content": f"""Search the inventory with this query: {query}
                    
                    Provide:
                    1. Relevant products matching the search
                    2. Current stock levels
                    3. Recent transaction history
                    4. Any relevant insights or recommendations"""}
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            return response.choices[0].message.content, None
        except Exception as e:
            return None, str(e)
    
    def generate_inventory_report(self) -> Tuple[Optional[str], Optional[str]]:
        """Generate a comprehensive inventory report using the model."""
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.agent_system_prompt},
                    {"role": "user", "content": """Generate a comprehensive inventory report including:
                    1. Overall inventory health
                    2. Products at risk of stockout
                    3. Overstocked items
                    4. Demand trends
                    5. Recommendations for optimization"""}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            return response.choices[0].message.content, None
        except Exception as e:
            return None, str(e) 