# Supply-bot

Supply-bot is an AI-powered inventory management system that leverages GPT models to provide intelligent inventory analysis, demand prediction, and optimization recommendations.

## Features

- **Intelligent Inventory Analysis**: Analyze inventory patterns and predict demand using AI
- **Data Processing**: Support for multiple data formats (CSV, Excel, JSON)
- **Demand Prediction**: AI-powered forecasting for optimal stock levels
- **Inventory Search**: Intelligent search functionality for inventory items
- **Embedding-backed Search**: Semantic retrieval ranks products by meaning before the AI responds
- **Comprehensive Reporting**: Generate detailed inventory reports and insights
- **Fine-tuning Capabilities**: Customize the AI model with your specific inventory data

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Kthecodeer2/Supply-bot.git
cd Supply-bot
```

1. Create a virtual environment (recommended):

```bash
python -m venv .venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Create a `.env` file in the project root with your OpenAI API key and a random secret key:

``` envfile
OPENAI_API_KEY=your_api_key_here
SUPPLYBOT_EMBEDDING_MODEL=google/gemini-embedding-2
Secret-Key=Key-Goes-Here
DATABASE_URL=sqlite:///inventory.db
```

``` bash
cd frontend
npm install
```

## Usage

1. Start the Flask backend application:

```bash
python app.py
```

Start the frontend:

```bash
cd frontend
npm run dev
```

1. Access the web interface at `http://localhost:5000`
2. Upload your inventory data in one of the supported formats (CSV, Excel, or JSON)
3. Use the interface to:

   - Process and analyze inventory data
   - Generate demand predictions
   - Search inventory items with semantic matching
   - Generate comprehensive reports

The search layer now uses the cloud embedding model `google/gemini-embedding-2` for semantic ranking, and it automatically falls back to recomputing any legacy stored vectors that no longer match the current embedding shape.

## Data Processing

The system supports three types of data:

- **Transactions**: Historical transaction data
- **Products**: Product catalog information
- **Sales**: Sales data and trends

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository.
