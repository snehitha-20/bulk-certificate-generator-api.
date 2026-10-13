# Bulk Certificate Generator API

## Project Overview

The Bulk Certificate Generator API is a backend application built using Python and FastAPI that generates PDF certificates for multiple recipients. Users can submit certificate generation requests containing event details and recipient information. The API generates individual PDF certificates, stores job and certificate records in an SQLite database, and provides endpoints to retrieve job details and download generated certificates.

## Features

- **Bulk Certificate Generation:** Generate PDF certificates for multiple recipients in a single request.
- **REST API:** Create and manage certificate generation jobs through FastAPI endpoints.
- **PDF Generation:** Generate personalized certificates using ReportLab.
- **Data Validation:** Validate recipient names, email addresses, event names, dates, and recipient lists using Pydantic.
- **Database Management:** Store job details and certificate statuses in SQLite.
- **Job Tracking:** Retrieve individual job details and view all submitted jobs.
- **Certificate Download:** Download generated certificates as PDF files.
- **Error Handling:** Handle invalid requests and missing jobs or certificates with appropriate HTTP status codes.
- **Automated Testing:** Test API endpoints and certificate generation functionality using pytest.

## Technologies Used

- Python
- FastAPI
- Pydantic
- SQLite
- ReportLab
- Uvicorn
- Pytest
- HTTPX
- Git and GitHub

## Project Structure

```text
Bulk-cert/
├── main.py
├── test/
│   └── test_main.py
├── requirements.txt
├── README.md
├── .gitignore
└── generated_certificates/
```

The `certificates.db` database and generated PDF files are created locally when the application runs. They do not need to be committed to GitHub.

## Installation and Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_REPOSITORY_FOLDER>
```

Replace the placeholders with your actual GitHub repository URL and folder name.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Start the API server

```bash
python -m uvicorn main:app --reload
```

The API will run locally at:

`http://127.0.0.1:8000`

Open the interactive API documentation at:

`http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check whether the API is running |
| POST | `/jobs` | Create a certificate generation job |
| GET | `/jobs` | Retrieve all certificate generation jobs |
| GET | `/jobs/{job_id}` | Retrieve details of a specific job |
| GET | `/certificates/{certificate_id}/download` | Download a generated certificate as a PDF |

## Example Request

Send a POST request to `/jobs` with the following JSON body:

```json
{
  "event_name": "Python Workshop",
  "event_date": "2026-10-13",
  "recipients": [
    {
      "name": "Ananya Sharma",
      "email": "ananya@example.com"
    },
    {
      "name": "Rahul Kumar",
      "email": "rahul@example.com"
    }
  ]
}
```

The API validates the request, creates a job, generates a separate PDF certificate for each recipient, and returns the job ID, processing status, success and failure counts, and certificate IDs.

Use the returned certificate ID with the download endpoint to retrieve the corresponding PDF.

## Database Design

The application uses SQLite with two tables:

- **Jobs:** Stores event details, job status, total recipients, successful certificates, and failed certificates.
- **Certificates:** Stores certificate IDs, associated job IDs, recipient information, generation status, PDF file paths, and error details.

## Running Automated Tests

Run the tests from the project root directory:

```bash
python -m pytest test -v
```

The test suite checks the home endpoint, job creation, input validation, job retrieval, and certificate downloads.

**Current test result:** 8 tests passed.

## Future Enhancements

- Background processing for large certificate batches.
- Authentication and authorization.
- Customizable certificate templates and branding.
- Email delivery of generated certificates.
- Retry mechanisms and improved job monitoring.

## Author

Developed as a backend API project to practice REST API development, PDF generation, database integration, input validation, and automated testing.
