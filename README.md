# Bulk Certificate Generator API

A web-based application that generates PDF certificates in bulk for multiple recipients. Users can enter event details, add recipient names and email addresses, generate certificates, download the generated PDFs, and view previously created certificate jobs.

The project combines a **FastAPI backend, a simple HTML/CSS/JavaScript frontend, ReportLab PDF generation, and an SQLite database**.

## Features

- **Bulk Certificate Generation:** Generate certificates for multiple recipients in one request.
- **Web Interface:** Enter event details and manage recipient information through a user-friendly interface.
- **PDF Generation:** Create downloadable PDF certificates using Python and ReportLab.
- **Input Validation:** Validate event details, recipient information, and email addresses.
- **Job Management:** Create and track certificate-generation jobs.
- **Database Storage:** Store job details and certificate records in SQLite.
- **Certificate Downloads:** Download individual generated certificates.
- **Job History:** View previous jobs and inspect their details.
- **REST API:** Access certificate-generation functionality through FastAPI endpoints.
- **Automated Testing:** Verify API functionality and error handling using pytest.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend development |
| FastAPI | REST API development |
| Uvicorn | Run the application server |
| Pydantic | Request validation |
| ReportLab | Generate PDF certificates |
| SQLite | Store job and certificate information |
| HTML | Structure the frontend |
| CSS | Style the web interface |
| JavaScript | Handle form submissions and API requests |
| Pytest | Automated testing |
| HTTPX | Test API endpoints |
| Git and GitHub | Version control and source-code hosting |

## Project Structure

```text
bulk-certificate-generator-api/
│
├── main.py                 # FastAPI application and API endpoints
├── test_main.py            # Automated API tests
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── .gitignore              # Files excluded from Git
│
├── static/
│   ├── index.html          # Frontend webpage
│   ├── style.css           # Frontend styling
│   └── script.js           # Frontend logic and API integration
│
├── certificates/            # Generated PDF files, if configured
└── certificates.db          # SQLite database, if configured
```

**Note:** The database and generated PDF directories may be created automatically when the application runs. Their actual locations depend on the configuration in `main.py`. Do not commit generated files or the database unless your project specifically requires them.

## How the Application Works

1. The user opens the web application in a browser.
2. The user enters the event name and event date.
3. The user adds the names and email addresses of the recipients.
4. JavaScript collects the form data and sends a POST request to the FastAPI backend.
5. FastAPI validates the incoming request using Pydantic.
6. The backend creates a job record in SQLite.
7. ReportLab generates a PDF certificate for each valid recipient.
8. Certificate information and generation results are stored in the database.
9. The frontend displays the job results and available certificate download links.
10. The user can revisit previous jobs and download generated certificates.

## Prerequisites

Install the following before running the project:

- Python 3.10 or later, compatible with the installed dependencies
- Visual Studio Code
- Git
- A modern web browser

The commands below use Windows Command Prompt or the VS Code terminal.

## Installation and Setup

### 1. Clone the repository

Replace the example URL with your actual GitHub repository URL.

```bash
git clone https://github.com/YOUR_USERNAME/bulk-certificate-generator-api.git
cd bulk-certificate-generator-api
```

Alternatively, open your existing project folder in VS Code.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

For Windows Command Prompt:

```cmd
.venv\Scripts\activate
```

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run the project's virtual-environment Python executable directly instead:

```powershell
.\.venv\Scripts\python.exe --version
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Start the application

From the project root directory, run:

```bash
python -m uvicorn main:app --reload
```

The application should be available at:

- **Web frontend:** http://127.0.0.1:8000/
- **Interactive API documentation:** http://127.0.0.1:8000/docs
- **Alternative API documentation:** http://127.0.0.1:8000/redoc

Keep the terminal running while using the application.

## Using the Web Application

1. Open http://127.0.0.1:8000/ in your browser.
2. Enter the event name and event date.
3. Add one or more recipients.
4. Enter each recipient's name and email address.
5. Select the certificate-generation button.
6. Review the generation results.
7. Download the generated PDF certificates.
8. Use the job-history section to view previous jobs and inspect their details.

## API Endpoints

The backend provides the following endpoints.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Serves the web frontend |
| POST | `/jobs` | Creates a certificate-generation job |
| GET | `/jobs` | Lists existing jobs |
| GET | `/jobs/{job_id}` | Retrieves details of a specific job |
| GET | `/certificates/{certificate_id}/download` | Downloads a generated certificate |

For exact request and response schemas, open the interactive API documentation at `/docs` while the server is running.

## Example API Request

**Endpoint:** `POST /jobs`

**Request body:**

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

This example requests certificates for two recipients attending the same event. The actual date format and field validation must match the Pydantic models defined in `main.py`.

## Database Design

The application uses SQLite to persist certificate-generation information.

### Jobs table

Stores information about each bulk-generation request, such as event details, job status, and generation counts, according to the fields defined in the application.

### Certificates table

Stores certificate-level information associated with a job, such as recipient details, certificate identifiers, generation status, and the generated PDF file path.

The certificates are associated with their corresponding job so that the application can retrieve job details and provide individual downloads.

## Frontend and Backend Integration

The frontend is implemented using HTML, CSS, and JavaScript.

- `index.html` defines the form, recipient fields, results area, and job history.
- `style.css` provides the layout, colors, spacing, and responsive styling.
- `script.js` adds recipient fields, submits requests to the backend, displays results, retrieves job history, and creates certificate download links.

FastAPI serves the frontend files from the `static/` directory. This allows the frontend and backend to run together on the same local server without requiring a separate frontend development server.

## Running Automated Tests

Run the tests from the project root:

```bash
python -m pytest -v
```

The test suite checks core functionality, including:

- Home page response
- Successful job creation
- Invalid email handling
- Empty recipient validation
- Retrieving an unknown job
- Listing jobs
- Downloading a certificate
- Handling an unknown certificate

**Important:** If the root endpoint now serves HTML instead of JSON, update the home-page test in `test_main.py` to verify the HTML response and a page element such as `Certificate Studio`.

Example:

```python
def test_home_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Certificate Studio" in response.text
```

Use the actual heading or text present in your `index.html`.

## Error Handling and Validation

The application is designed to handle common invalid requests, including:

- Missing or invalid recipient information
- Invalid email addresses
- Empty recipient lists
- Requests for jobs that do not exist
- Requests to download certificates that do not exist

FastAPI returns HTTP responses for API errors, while the frontend should display useful messages to users.

## Future Enhancements

Possible improvements include:

- Custom certificate templates and branding
- Organization logos, signatures, and QR codes
- ZIP downloads for all certificates in a job
- Background processing for large batches
- Email delivery of generated certificates
- Authentication and role-based access control
- Job progress tracking
- Deployment to a cloud hosting platform
- Improved logging and monitoring

These are potential future improvements and are not necessarily implemented in the current version.

## Learning Outcomes

This project provides practical experience with:

- Designing and implementing REST APIs
- Validating request data with Pydantic
- Generating PDF documents programmatically
- Integrating a frontend with a Python backend
- Persisting application data with SQLite
- Handling API errors and file downloads
- Writing automated tests
- Managing code with Git and GitHub

## Author

**Developed as a Python backend and full-stack web development project.**

GitHub:https://github.com/snehitha-20/bulk-certificate-generator-api


---

*This application is intended as a project implementation and can be extended for event organizers, workshops, training programs, and other certificate-based activities.*
