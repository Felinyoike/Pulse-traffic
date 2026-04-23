# Pulse Traffic API - Backend

The Pulse Traffic API is a robust backend service designed for simulated traffic data ingestion, historical tracking, and congestion prediction. Built with **FastAPI** and **SQLAlchemy**, it provides a high-performance REST API to receive sensor data (like vehicle count, speed, and density), store it in a relational database, and generate future traffic congestion predictions based on moving averages.

## Key Features

- **Traffic Data Ingestion:** Securely receive and validate traffic readings from simulated sensor nodes.
- **Data Validation:** Strict QA validation utilizing Pydantic to ensure no negative values and accurate density percentages.
- **Congestion Prediction:** Automatically calculates a 1-hour future traffic congestion level (High, Medium, Low) and confidence score for any specific node based on recent speed trends.
- **Interactive API Docs:** Built-in Swagger UI and ReDoc for easy API exploration and testing.

## Technology Stack

- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Data Validation:** Pydantic
- **Server:** Uvicorn

---

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.8 or higher
- Git

### Installation Steps

**1. Clone the repository**

First, clone the project from GitHub to your local machine:
```bash
git clone https://github.com/linetmungai/Pulse-traffic.git
```

**2. Navigate to the backend directory**

Change your directory to the `backend` folder where the API code resides:
```bash
cd Pulse-traffic/backend
```

**3. Create a Virtual Environment**

It is best practice to use a virtual environment to manage dependencies. Create one using the following command:
```bash
python -m venv venv
```

**4. Activate the Virtual Environment**

- On **Windows**:
  ```bash
  venv\Scripts\activate
  ```
- On **macOS and Linux**:
  ```bash
  source venv/bin/activate
  ```

**5. Install Requirements**

Install all required Python packages (like FastAPI, Uvicorn, and SQLAlchemy) using the provided `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### Running the Application

Once everything is installed and your virtual environment is active, you can run the server locally. Ensure you are inside the `backend` directory and run:

```bash
uvicorn main:app --reload
```

The `--reload` flag enables auto-reloading, meaning the server will automatically restart if you make changes to the code.

You can now access the interactive API documentation by navigating to http://127.0.0.1:8000/docs in your web browser.

---

## Available Endpoints

- `POST /traffic-data` - Ingest new traffic data from a sensor node.
- `GET /traffic-data` - Retrieve a list of historical traffic records (supports pagination and filtering by `node_id`).
- `POST /predict/{node_id}` - Generate a congestion prediction for a given node.

### Traffic payload contract

The ingestion endpoint accepts `vehicle_count`, `speed`, `density`, and `timestamp`. The backend also accepts an optional `node_id` and defaults it to `simulator` when omitted.

Accepted ranges:

- `vehicle_count`: 0 to 200
- `speed`: 0 to 120
- `density`: 0 to 1