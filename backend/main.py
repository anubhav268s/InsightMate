from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import uuid
from datetime import datetime

# Import processing modules
from services.ai_service import AIService
from services.file_service import FileService
from services.data_service import DataService
from config import settings

app = FastAPI(
    title="Insightmate API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ai_service = AIService()
file_service = FileService()
data_service = DataService()

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    mode: str = "general"  # "general" or "personalized"

class ChatResponse(BaseModel):
    response: str
    mode: str
    timestamp: str

class PortfolioLink(BaseModel):
    url: str
    type: str  # "linkedin", "github", "website"
    description: Optional[str] = None

class UserData(BaseModel):
    portfolio_links: List[PortfolioLink] = []
    uploaded_files: List[str] = []

@app.get("/")
async def root():
    return {"message": "Insightmate API is running!"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """Handle chat messages for both general and personalized modes"""
    try:
        if chat_message.mode == "general":
            response = await ai_service.general_chat(chat_message.message)
        else:
            # Get user data for personalized response
            user_data = data_service.get_user_data()
            response = await ai_service.personalized_chat(
                chat_message.message, user_data
            )
        return ChatResponse(
            response=response,
            mode=chat_message.mode,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file uploads (resumes, certificates, etc.)"""
    try:
        # Save uploaded file
        file_path = await file_service.save_file(file)
        # Process the file and extract content
        processed_data = await file_service.process_file(file_path)
        # Store the processed data
        data_service.add_file_data(file.filename, processed_data)
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "file_path": file_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/portfolio-links")
async def add_portfolio_link(link: PortfolioLink):
    """Add portfolio links (LinkedIn, GitHub, etc.)"""
    try:
        # Process the link and extract content
        processed_data = await file_service.process_url(link.url)
        # Store the link data
        data_service.add_portfolio_link(link, processed_data)
        return {
            "message": "Portfolio link added successfully",
            "url": link.url,
            "type": link.type
        }
    except Exception as e:
        print(f"Error adding portfolio link: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user-data")
async def get_user_data():
    """Get all user data (files and links)"""
    try:
        return data_service.get_user_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/files/{filename}")
async def delete_file(filename: str):
    """Delete uploaded file"""
    try:
        data_service.delete_file(filename)
        file_service.delete_file(filename)
        return {"message": f"File {filename} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/portfolio-links/{link_id}")
async def delete_portfolio_link(link_id: str):
    """Delete portfolio link"""
    try:
        data_service.delete_portfolio_link(link_id)
        return {"message": "Portfolio link deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "ai_service": "active",
            "file_service": "active",
            "data_service": "active"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print(f"Starting Insightmate API server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)