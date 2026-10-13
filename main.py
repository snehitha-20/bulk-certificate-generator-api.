
import sqlite3
import uuid
from pathlib import Path

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas


import json
from datetime import date
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field, field_validator

from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
# -----------------------------------
# 1. Project and database configuration
# -----------------------------------

BASE_DIR = Path(__file__).resolve().parent

# Database file
DB_PATH = BASE_DIR / "certificates.db"

# Folder for generated PDF certificates
OUTPUT_DIR = BASE_DIR / "generated_certificates"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)





class Recipient(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr

    @field_validator("name")
    @classmethod
    def check_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Recipient name cannot be empty")

        return value



class JobRequest(BaseModel):
    event_name: str = Field(min_length=1, max_length=200)
    event_date: date
    recipients: list[Recipient] = Field(min_length=1, max_length=1000)

    @field_validator("event_name")
    @classmethod
    def check_event_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Event name cannot be empty")

        return value





app = FastAPI(
        title="Bulk Certificate Generator API",
        description="Generate certificates for multiple recipients",
        version="1.0.0"
    )

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)




@app.on_event("startup")
def startup_event():
    init_db()

    
# -----------------------------------
# 2. Connect to the database
# -----------------------------------

def connect_db():
    conn = sqlite3.connect(DB_PATH, timeout=30)

    # Access columns by their names
    conn.row_factory = sqlite3.Row

    # Enable foreign key enforcement
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# -----------------------------------
# 3. Create database tables
# -----------------------------------

def init_db():
    conn = connect_db()

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                event_name TEXT NOT NULL,
                event_date TEXT NOT NULL,
                status TEXT NOT NULL,
                total INTEGER NOT NULL,
                succeeded INTEGER DEFAULT 0,
                failed INTEGER DEFAULT 0
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS certificates (
                id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                recipient_json TEXT NOT NULL,
                status TEXT NOT NULL,
                file_path TEXT,
                error TEXT,
                FOREIGN KEY(job_id) REFERENCES jobs(id)
            )
        """)

        conn.commit()
        print("Database tables created successfully!")

    finally:
        conn.close()


# -----------------------------------
# 4. Generate a certificate PDF
# -----------------------------------

def generate_pdf(name, event_name, event_date, output_path):

    # Set the page size to landscape A4
    page_size = landscape(A4)
    width, height = page_size

    # Create the PDF
    pdf = canvas.Canvas(str(output_path), pagesize=page_size)

    # Certificate border
    pdf.setStrokeColor(HexColor("#19365C"))
    pdf.setLineWidth(4)
    pdf.rect(25, 25, width - 50, height - 50)

    # Certificate title
    pdf.setFillColor(HexColor("#19365C"))
    pdf.setFont("Helvetica-Bold", 27)

    pdf.drawCentredString(
        width / 2,
        height - 105,
        "CERTIFICATE OF PARTICIPATION"
    )

    # Introductory text
    pdf.setFillColor(HexColor("#222222"))
    pdf.setFont("Helvetica", 16)

    pdf.drawCentredString(
        width / 2,
        height - 160,
        "This certificate is presented to"
    )

    # Recipient name
    pdf.setFont("Helvetica-Bold", 25)

    pdf.drawCentredString(
        width / 2,
        height - 210,
        name
    )

    # Event name
    pdf.setFont("Helvetica", 15)

    pdf.drawCentredString(
        width / 2,
        height - 255,
        f"For participating in {event_name}"
    )

    # Event date
    pdf.drawCentredString(
        width / 2,
        height - 290,
        f"Date: {event_date}"
    )

    # Signature text
    pdf.setFont("Helvetica-Oblique", 12)

    pdf.drawCentredString(
        width / 2,
        65,
        "Authorized by the event organizer"
    )

    # Save the PDF file
    pdf.save()




@app.get("/", include_in_schema=False)
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/jobs", status_code=201)
def create_job(request: JobRequest):
    # Create a unique ID for the job
    job_id = str(uuid.uuid4())
    event_date_text = request.event_date.isoformat()

    succeeded = 0
    failed = 0
    results = []

    # Save the initial job information
    conn = connect_db()
    try:
        conn.execute(
            """
            INSERT INTO jobs
            (id, event_name, event_date, status, total, succeeded, failed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job_id,
                request.event_name,
                event_date_text,
                "PROCESSING",
                len(request.recipients),
                0,
                0,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    # Generate a PDF for each recipient
    for recipient in request.recipients:
        certificate_id = str(uuid.uuid4())

        try:
            output_path = OUTPUT_DIR / f"{certificate_id}.pdf"

            generate_pdf(
                name=recipient.name,
                event_name=request.event_name,
                event_date=event_date_text,
                output_path=output_path,
            )

            status = "SUCCEEDED"
            file_path = str(output_path)
            error = None
            succeeded += 1

        except Exception as exc:
            status = "FAILED"
            file_path = None
            error = str(exc)[:1000]
            failed += 1

        # Save the certificate result in the database
        conn = connect_db()
        try:
            conn.execute(
                """
                INSERT INTO certificates
                (id, job_id, recipient_json, status, file_path, error)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    certificate_id,
                    job_id,
                    recipient.model_dump_json(),
                    status,
                    file_path,
                    error,
                ),
            )
            conn.commit()
        finally:
            conn.close()

        results.append(
            {
                "certificate_id": certificate_id,
                "recipient_name": recipient.name,
                "status": status,
                "error": error,
            }
        )

    # Determine the final job status
    if failed == 0:
        final_status = "COMPLETED"
    elif succeeded == 0:
        final_status = "FAILED"
    else:
        final_status = "COMPLETED_WITH_ERRORS"

    # Update the job summary in the database
    conn = connect_db()
    try:
        conn.execute(
            """
            UPDATE jobs
            SET status = ?, succeeded = ?, failed = ?
            WHERE id = ?
            """,
            (final_status, succeeded, failed, job_id),
        )
        conn.commit()
    finally:
        conn.close()

    # Return the job result
    return {
        "job_id": job_id,
        "status": final_status,
        "total": len(request.recipients),
        "succeeded": succeeded,
        "failed": failed,
        "certificates": results,
    }




    
@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    # Step 1: Connect to the database
    conn = connect_db()

    try:
        # Step 2: Find the requested job
        job = conn.execute(
            "SELECT * FROM jobs WHERE id = ?",
            (job_id,)
        ).fetchone()

        # Step 3: Return 404 if the job does not exist
        if job is None:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        # Step 4: Get all certificates belonging to this job
        certificates = conn.execute(
            """
            SELECT id, recipient_json, status, file_path, error
            FROM certificates
            WHERE job_id = ?
            """,
            (job_id,)
        ).fetchall()

        # Step 5: Prepare and return the response
        return {
            "job_id": job["id"],
            "event_name": job["event_name"],
            "event_date": job["event_date"],
            "status": job["status"],
            "total": job["total"],
            "succeeded": job["succeeded"],
            "failed": job["failed"],
            "certificates": [
                {
                    "certificate_id": cert["id"],
                    "recipient": json.loads(cert["recipient_json"]),
                    "status": cert["status"],
                    "file_path": cert["file_path"],
                    "error": cert["error"],
                }
                for cert in certificates
            ],
        }

    finally:
        # Step 6: Always close the database connection
        conn.close()






@app.get("/certificates/{certificate_id}/download")
def download_certificate(certificate_id: str):
    # Connect to the database
    conn = connect_db()

    try:
        # Find the certificate
        certificate = conn.execute(
            """
            SELECT file_path, status
            FROM certificates
            WHERE id = ?
            """,
            (certificate_id,),
        ).fetchone()

        # Check whether the certificate exists
        if certificate is None:
            raise HTTPException(
                status_code=404,
                detail="Certificate not found",
            )

        # Ensure generation was successful
        if certificate["status"] != "SUCCEEDED":
            raise HTTPException(
                status_code=409,
                detail="Certificate was not generated successfully",
            )

        file_path = certificate["file_path"]

    finally:
        conn.close()

    # Check whether the PDF file exists
    if not file_path or not Path(file_path).is_file():
        raise HTTPException(
            status_code=404,
            detail="Certificate PDF file not found",
        )

    # Return the PDF as a downloadable file
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"certificate_{certificate_id}.pdf",
    )






@app.get("/jobs")
def get_all_jobs():
    conn = connect_db()

    try:
        # Retrieve all jobs, newest first
        rows = conn.execute(
            """
            SELECT id, event_name, event_date, status,
                   total, succeeded, failed
            FROM jobs
            ORDER BY rowid DESC
            """
        ).fetchall()

        # Convert database rows into a JSON response
        jobs = [
            {
                "job_id": row["id"],
                "event_name": row["event_name"],
                "event_date": row["event_date"],
                "status": row["status"],
                "total": row["total"],
                "succeeded": row["succeeded"],
                "failed": row["failed"],
            }
            for row in rows
        ]

        return {
            "total_jobs": len(jobs),
            "jobs": jobs,
        }

    finally:
        conn.close()




# -----------------------------------
# 5. Run a test
# -----------------------------------

if __name__ == "__main__":

    # Initialize the database
    init_db()

    # Generate a sample certificate
    sample_path = OUTPUT_DIR / "sample.pdf"

    generate_pdf(
        name="Ananya Sharma",
        event_name="Python Workshop",
        event_date="2026-10-13",
        output_path=sample_path
    )

    print("Sample certificate generated successfully!")
    print("PDF location:", sample_path)

   