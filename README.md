# E-commerce Agent

A FastAPI-based agent that translates natural language queries into SQL to interact with an e-commerce database, providing answers and visualizations.

## Features

*   **Natural Language to SQL Translation**: Uses the Groq API with Llama 3 to convert user questions into executable SQL queries.
*   **FastAPI Backend**: A robust backend serving the UI and handling API requests with rate limiting.
*   **Dynamic Visualizations**: Generates charts (bar, pie, line) based on the query results using Matplotlib.
*   **Simple Web Interface**: A clean and simple UI for asking questions and viewing results.

## Tech Stack

*   **Backend**: FastAPI, Uvicorn
*   **LLM**: Groq API (Llama 3)
*   **Data Handling**: Pandas
*   **Visualization**: Matplotlib
*   **Frontend**: HTML, CSS, JavaScript

## Project Structure

```
├── api
│   └── main.py         # FastAPI application, endpoints
├── config
│   └── settings.py     # Pydantic settings management
├── csv
│   └── *.csv           # Sample CSV data files
├── db
│   ├── connection.py   # Database connection
│   └── loader.py       # Loads CSV data into the database
├── llm
│   ├── groq_client.py  # Groq API client
│   └── sql_translator.py # Handles NL to SQL translation
├── static
│   └── index.html      # Frontend UI
├── visualizer
│   └── plotter.py      # Generates plots from data
├── .env.example        # Example environment file
├── run.py              # Application entry point
├── requirements.txt    # Project dependencies
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
    Create a `.env` file in the project root and add your Groq API key:
    ```
    GROQ_API_KEY="your_groq_api_key"
    ```

4.  **Run the application:**
    ```bash
    python3 run.py
    ```
    The application will be available at `http://0.0.0.0:8000`.

## Usage

1.  Access the web interface at `http://0.0.0.0:8000/ui/`.
2.  Enter a question about the e-commerce data in the text box (e.g., "What are the total sales per month?").
3.  Click "Ask" to see the generated SQL query, the result table, and a visualization if applicable.

## API Endpoint

### `POST /api/ask`

Accepts a natural language question and returns the SQL translation, query result, and an optional visualization.

**Request Body:**

```json
{
  "question": "How many orders were placed last month?"
}
```

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

## Code Snippets

### Agent Instructions (`llm/sql_translator.py`)

The system prompt that guides the LLM to generate SQL queries.

```python
SYSTEM_PROMPT = (
    "You are an expert SQL developer. Your task is to translate a given natural language question "
    "into a SQL query based on the provided database schema. Only return the SQL query, with no additional text or explanations."
)
```

### API Endpoint Logic (`api/main.py`)

The FastAPI endpoint that orchestrates the translation and database query process.

```python
@api_router.post("/ask", response_model=QueryResult)
async def ask_question(request: Request, question: Question):
    # ... (rate limiting logic)
    translator = SQLTranslator(db_connection)
    try:
        sql_query, result, plot_path = await translator.translate_to_sql_and_execute(
            question.question
        )
        return QueryResult(
            sql_query=sql_query,
            result=result,
            visualization_path=plot_path,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```