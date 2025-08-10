# CodeGuard - Code Analysis System 🚀


## Overview 🔎
CodeGuard is a backend system designed to analyze Python code quality automatically every time the user runs `wit push`.  
It integrates a simplified version control system (`wit`) with a FastAPI backend that performs code analysis, detects common issues, and generates visual graphs to provide insights into code health.

The system simulates a basic Continuous Integration (CI) focused on maintaining high-quality code.

---


## Technologies Used 🛠️
- Python 3.x  
- FastAPI (backend server)  
- AST (Abstract Syntax Tree) for static code analysis  
- Matplotlib for generating visual graphs  

---


## Project Structure 📂

codeguard/  
│  
├── app/  
│   ├── routers/  
│   │   └── analysis.py         # API endpoint definitions  
│   ├── services/  
│   │   ├── analyzer.py         # Code analysis logic using AST  
│   │   ├── graph_generator.py  # Functions to create matplotlib graphs  
│   │   └── utils.py            # Helper utilities  
│   └── main.py                 # FastAPI app startup  
│  
├── requirements.txt            # Python dependencies  
└── README.md                   # This documentation file  

---


## Installation and Setup ⚙️

1. Clone the repository  

```bash
git clone https://github.com/HadassaAvimorNew/codeguard.git  
cd codeguard  
```
2. Create and activate a virtual environment
```bash
python -m venv venv  
# On Windows  
venv\Scripts\activate  
# On macOS/Linux  
source venv/bin/activate  
```
3. Install required dependencies
```bash
pip install -r requirements.txt  
```


## Running the Server ▶️

Start the FastAPI server by running:

```bash
uvicorn app.main:app --reload
```
The server will be available at: http://localhost:8000

---


## API Endpoints 📡

### POST /analyze

- Description: Accepts Python files, analyzes the code, and returns PNG images with graphs that visualize:  
  - Distribution of function lengths (Histogram)  
  - Number of issues per issue type (Pie Chart)  
  - Number of issues per file (Bar Chart)  

- Request:  
  - Accepts multiple Python files as form-data.

- Response:  
  - PNG images representing the generated graphs.



### POST /alerts

- Description: Accepts Python files and returns a JSON response listing detected issues, including:  
  - Functions longer than 20 lines  
  - Files longer than 200 lines  
  - Unused variables  
  - Missing docstrings  
  - (Bonus) Variables named with non-English letters (e.g., Hebrew)  

- Request:  
  - Accepts multiple Python files as form-data.

- Response:  
  - JSON object containing warnings per file and issue type.

---


## Usage with wit push 🔁

When the user executes `wit push`, the committed Python files are sent to the CodeGuard backend. The backend analyzes the code, generates warnings, and produces visual graphs that help maintain code quality across commits.

---


## Bonus Feature 💡

The system detects variable names written in non-English characters (for example, Hebrew letters) and issues warnings about their usage to encourage consistency and readability.
