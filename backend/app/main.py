from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
import uvicorn
import os
import logging 

app = FastAPI(title="Auto Verification Chatbot", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(chat_router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Mount static files and serve index.html at root
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend")
print(f"Looking for frontend at: {frontend_path}")

if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    
    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_path, "index.html"))
    
    print(f"✅ Serving chatbot interface from: {frontend_path}")
else:
    print(f"⚠️  Frontend directory not found: {frontend_path}")
    
    @app.get("/")
    async def root():
        return {
            "message": "Auto Verification Chatbot API is running!",
            "docs": "/docs",
            "frontend_path_expected": frontend_path,
            "instructions": "Create the frontend directory and add index.html file"
        }

# add logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)