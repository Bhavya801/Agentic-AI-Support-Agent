from fastapi import APIRouter
from services.email_handler import process_emails_job

router = APIRouter()

@router.get("/support/process-mail", tags=["Email Processing"])
def process_mail():
    """
    API endpoint to trigger the email processing job.
    This is intended to be called by an external cron service (like cron or a scheduler).
    """
    process_emails_job()
    return {"message": "Email processing job triggered successfully."}
