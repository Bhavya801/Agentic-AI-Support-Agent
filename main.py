import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# Import the new email router
from routes.email_router import router as email_router

# --- FastAPI Setup ---
app = FastAPI()

# Include the email router
app.include_router(email_router)

# Expose a simple health check endpoint for the Uvicorn server
@app.get("/")
def read_root():
    """
    A simple endpoint to confirm the service is running.
    """
    return {"message": "AI Support Agent Service is running. Email processing is handled by a separate cron job."}

@app.get("/redocs", response_class=HTMLResponse)
def get_redoc_docs():
    """
    Serves the Redoc HTML documentation page.
    """
    with open("docs/index.html", "r") as f:
        html_content = f.read()
    return html_content

# This section is for local development with `uvicorn main:app --reload`
if __name__ == "__main__":
    # We will simply execute the Uvicorn server when the file is run directly.
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3218)

