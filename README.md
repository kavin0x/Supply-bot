#NOTE:
This project is still way in beta, hardly working, feel free to help me work on this.

# Supply-bot

Supply-bot is an AI-powered inventory management system that leverages GPT models to provide intelligent inventory analysis, demand prediction, and optimization recommendations.

## Features

- **Intelligent Inventory Analysis**: Analyze inventory patterns and predict demand using AI
- **Data Processing**: Support for multiple data formats (CSV, Excel, JSON)
- **Demand Prediction**: AI-powered forecasting for optimal stock levels
- **Inventory Search**: Intelligent search functionality for inventory items
- **Comprehensive Reporting**: Generate detailed inventory reports and insights
- **Fine-tuning Capabilities**: Customize the AI model with your specific inventory data

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Kthecodeer2/Supply-bot.git
cd Supply-bot
```

2. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your OpenAI API key and a random secret key:

```
OPENAI_API_KEY=your_api_key_here
Secret-Key=Key-Goes-Here
```

## Usage

1. Start the Flask application:

```bash
python app.py
```

2. Access the web interface at `http://localhost:5000`
3. Upload your inventory data in one of the supported formats (CSV, Excel, or JSON)
4. Use the interface to:

   - Process and analyze inventory data
   - Generate demand predictions
   - Search inventory items
   - Generate comprehensive reports

## Data Processing

The system supports three types of data:

- **Transactions**: Historical transaction data
- **Products**: Product catalog information
- **Sales**: Sales data and trends

## Dependencies

- Flask 3.0.2
- Pandas 2.2.1
- NumPy 1.26.4
- scikit-learn 1.4.1
- Matplotlib 3.8.3
- OpenAI API 1.12
- And other dependencies listed in requirements.txt

## Project Structure

```
Supply-bot/
├── app.py              # Main Flask application
├── gpt_model.py        # GPT model implementation
├── requirements.txt    # Project dependencies
├── .env               # Environment variables
├── training_data/     # Directory for training data
├── templates/         # Flask templates
└── instance/          # Database instance
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository.
