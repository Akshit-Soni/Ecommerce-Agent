# E-commerce Agent

A FastAPI-based agent that translates natural language queries into SQL to interact with an e-commerce database, providing answers and visualizations. This agent supports multiple LLM providers, including Groq, Ollama (for local models like `gemma:2b`), and Google's Gemini.

## Features

*   **Multi-Provider LLM Support**: Seamlessly switch between Groq, Ollama, and Gemini for natural language to SQL translation.
*   **Local LLM Integration**: Use local models via Ollama for offline and private data analysis.
*   **FastAPI Backend**: A robust backend serving the UI and handling API requests with rate limiting.
*   **Dynamic Visualizations**: Generates charts (bar, pie, line) based on the query results using Matplotlib.
*   **Interactive Web Interface**: A clean UI with a dropdown to select the LLM provider.

## Tech Stack

*   **Backend**: FastAPI, Uvicorn
*   **LLMs**:
    *   Groq API (Llama 3)
    *   Ollama (e.g., `gemma:2b`)
    *   Google Gemini
*   **Data Handling**: Pandas
*   **Visualization**: Matplotlib
*   **Frontend**: HTML, CSS, JavaScript

## Project Structure

```
├── api
│   └── main.py             # FastAPI application, endpoints
├── config
│   └── settings.py         # Pydantic settings management
├── csv
│   └── *.csv               # Sample CSV data files
├── db
│   ├── connection.py       # Database connection
│   └── loader.py           # Loads CSV data into the database
├── llm
│   ├── gemini_client.py    # Gemini API client
│   ├── groq_client.py      # Groq API client
│   ├── ollama_client.py    # Ollama client for local models
│   └── sql_translator.py   # Handles NL to SQL translation
├── static
│   └── index.html          # Frontend UI
├── visualizer
│   └── plotter.py          # Generates plots from data
├── .env.example            # Example environment file
├── run.py                  # Application entry point
├── requirements.txt        # Project dependencies
└── README.md
```

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd ecom-agent
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the project root and add your API keys. You only need to provide keys for the services you intend to use.
    ```
    GROQ_API_KEY="your_groq_api_key"
    GEMINI_API_KEY="your_gemini_api_key"
    ```

4.  **(Optional) Set up Ollama:**
    If you want to use a local model, make sure Ollama is installed and running. You can pull a model like `gemma:2b`:
    ```bash
    ollama pull gemma:2b
    ```

5.  **Run the application:**
    ```bash
    python run.py
    ```
    The application will be available at `http://localhost:8000`.

## Usage

1.  Access the web interface at `http://localhost:8000`.
2.  Select your desired LLM provider from the dropdown (Groq, Ollama, or Gemini).
3.  Enter a question about the e-commerce data in the text box (e.g., "What are the total sales per month?").
4.  Click "Ask" to see the generated SQL query, the result table, and a visualization if applicable.

## API Endpoint

### `POST /api/ask`

Accepts a natural language question and the selected provider, then returns the SQL translation, query result, and an optional visualization.

**Request Body:**

```json
{
  "question": "How many orders were placed last month?",
  "provider": "gemini"
}
```

**Available Providers:** `groq`, `ollama`, `gemini`

**Response Body:**

```json
{
  "sql_query": "SELECT count(*) FROM orders WHERE strftime('%Y-%m', order_date) = strftime('%Y-%m', 'now', '-1 month');",
  "result": [
    {
      "count(*)": 120
    }
  ],
  "visualization_path": "/static/plots/plot.png"
}
```