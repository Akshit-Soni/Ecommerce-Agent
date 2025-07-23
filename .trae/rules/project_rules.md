LLM IDE Project Instructions: E-commerce SQL+LLM Agent

Project Objective

This system should enable querying e-commerce-related business data via natural language, converting queries into SQL, and executing them against data provided in Google Sheets. It must operate locally (Ollama-based) for privacy while supporting Groq (for open-source testing) and Gemini (for fallback).

⸻

High-Level Architecture
	•	data_ingestion/: Parse and ingest Google Sheets/CSV
	•	db/: Auto-generate SQLite DB schema from data
	•	llm/: SQL generation + LLM abstraction
	•	api/: FastAPI service with rate-limited endpoints
	•	utils/: Logging, validation, and utility tools
	•	.env: Configuration for model provider and API keys

⸻

Required LLM Behavior

Core Behavior Rules
	•	Never hallucinate column names, metrics, or SQL structure.
	•	Always base queries and logic on the actual ingested dataset.
	•	Ask the user to confirm or define:
	•	Metrics
	•	Dimensions
	•	Custom aggregations or filters
	•	Use the provided CSV headers to dynamically build or validate SQL queries.

Model Usage Order
	1.	Groq + Mixtral: For default testing
	2.	Gemini Pro: If Groq fails or on request
	3.	Ollama + Mistral/Code Llama: For private, local execution

⸻

SQL Agent Responsibilities
	•	On receiving a query:
	1.	Parse user’s intent
	2.	Match with table columns
	3.	Generate validated SQL
	4.	Execute and return clean tabular results
	•	If the query is ambiguous:
	•	Ask clarifying questions
	•	If the query cannot be answered:
	•	Return a human-readable message explaining why

⸻

Data Handling Rules
	•	Accept CSVs from Google Sheets (via download or URL)
	•	Auto-detect headers, column types
	•	If metrics are undefined:
	•	Prompt user to specify metric columns
	•	If missing/null values:
	•	Log and clean or ask user how to handle

⸻

Code Generation Guidelines
	•	Code must be beginner-friendly, clean, and modular
	•	Always explain:
	•	What was added
	•	Why it works
	•	How to test it
	•	Do not duplicate logic across modules
	•	Reuse utility functions wherever possible

⸻

Error Handling Policy
	•	Do not patch errors blindly
	•	Log full tracebacks
	•	Explain:
	•	What caused the error
	•	Two or more ways to fix it
	•	Ask user how to proceed
	•	All exceptions must have readable messages for debugging

⸻

Component Reuse & Resolution Strategy
	•	Before building anything new:
	1.	Check existing components
	2.	Refactor or extend if possible
	•	Use chain-of-thought reasoning:
	•	What is the issue?
	•	What are the options?
	•	What is the optimal approach?

⸻

Rate Limiting & API Behavior
	•	Implement rate limiting on all endpoints using slowapi
	•	Provide:
	•	/health endpoint
	•	/ask or /query endpoint for LLM-powered queries
	•	/upload or /ingest endpoint for data
	•	Add logging and response time for every query

⸻

Deployment & Compatibility Notes
	•	Must run smoothly on MacBook Air M1
	•	Prefer libraries that are:
	•	Fast and efficient
	•	ARM-compatible
	•	Actively maintained
	•	Provide requirements.txt and env.sample

⸻

Logging and Observability
	•	Use logging module for all internal logs
	•	Track:
	•	API hits
	•	LLM call latency
	•	Query errors and resolutions
	•	Log should be concise but traceable

⸻

Security and Privacy
	•	Do not log sensitive data
	•	Do not send full datasets to external LLMs unless approved
	•	Warn user before performing any internet or cloud-based operation

⸻

User Instruction Flow
	1.	Ask user to upload CSV or provide Google Sheets link
	2.	Display preview of dataset and ask to confirm:
	•	Metrics
	•	Dimensions
	3.	Ask natural language query
	4.	Return result with SQL used
	5.	Ask if the answer was helpful or needs refining

⸻