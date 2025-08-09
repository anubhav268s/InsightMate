import os
import aiofiles
import uuid
from typing import Optional
from fastapi import UploadFile
import fitz  # PyMuPDF
import pdfplumber
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings


class FileService:
    def __init__(self):
        # Initialize upload directory
        self.upload_dir = settings.UPLOAD_DIRECTORY
        os.makedirs(self.upload_dir, exist_ok=True)
        # Allowed file types
        self.allowed_extensions = {
            '.pdf', '.txt', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif'
        }
        self.max_file_size = settings.MAX_FILE_SIZE

    async def save_file(self, file: UploadFile) -> str:
        """Save uploaded file to disk"""
        # Validate file
        if not self._is_allowed_file(file.filename):
            raise ValueError(f"File type not allowed: {file.filename}")
        # file.size is not available in UploadFile, so we need to read the content to check size
        content = await file.read()
        if len(content) > self.max_file_size:
            raise ValueError(f"File too large: {len(content)} bytes")
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        return file_path

    async def process_file(self, file_path: str) -> str:
        """Process uploaded file and extract text content"""
        file_extension = Path(file_path).suffix.lower()
        try:
            if file_extension == '.pdf':
                return await self.process_pdf(file_path)
            elif file_extension == '.txt':
                return await self.process_text(file_path)
            elif file_extension in ['.doc', '.docx']:
                return await self.process_document(file_path)
            elif file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
                return await self.process_image(file_path)
            else:
                return f"File type {file_extension} not supported for content extraction."
        except Exception as e:
            return f"Error processing file: {str(e)}"

    async def process_url(self, url: str) -> str:
        """Process URL and extract content"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            # Extract text
            text = soup.get_text()
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            # Limit text length
            if len(text) > 5000:
                text = text[:5000] + "... [Content truncated]"
            return text
        except requests.RequestException as e:
            return f"Error fetching URL: {str(e)}"
        except Exception as e:
            return f"Error processing URL content: {str(e)}"

    def delete_file(self, filename: str) -> bool:
        """Delete file from uploads directory"""
        try:
            # Find file in uploads directory
            for file in os.listdir(self.upload_dir):
                if file.startswith(filename.split('.')[0]):
                    file_path = os.path.join(self.upload_dir, file)
                    os.remove(file_path)
                    return True
            return False
        except Exception:
            return False

    async def process_pdf(self, file_path: str) -> str:
        """Extract text from PDF using PyMuPDF"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            # Fallback to pdfplumber if PyMuPDF fails
            if not text.strip():
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            return text.strip() if text.strip() else "No text content found in PDF."
        except Exception as e:
            return f"Error processing PDF: {str(e)}"

    async def process_text(self, file_path: str) -> str:
        """Process plain text file"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            return content
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                async with aiofiles.open(file_path, 'r', encoding='latin-1') as f:
                    content = await f.read()
                return content
            except Exception as e:
                return f"Error reading text file: {str(e)}"
        except Exception as e:
            return f"Error processing text file: {str(e)}"

    async def process_document(self, file_path: str) -> str:
        """Process Word documents (.doc, .docx)
        Note: This is a basic implementation. For better results, consider using python-docx for .docx files
        """
        try:
            # This is a placeholder implementation
            # In a real application, you would use libraries like python-docx
            return f"Document processing not fully implemented for: {file_path}"
        except Exception as e:
            return f"Error processing document: {str(e)}"

    async def process_image(self, file_path: str) -> str:
        """Process image files
        Note: This would require OCR capabilities for text extraction
        """
        try:
            # This is a placeholder implementation
            # In a real application, you would use OCR libraries like pytesseract
            file_size = os.path.getsize(file_path)
            return f"Image file processed. Size: {file_size} bytes. OCR not implemented yet."
        except Exception as e:
            return f"Error processing image: {str(e)}"

    def _is_allowed_file(self, filename: str) -> bool:
        """Check if file type is allowed"""
        if not filename:
            return False
        file_extension = Path(filename).suffix.lower()
        return file_extension in self.allowed_extensions

    def get_upload_stats(self) -> dict:
        """Get statistics about uploaded files"""
        try:
            files = os.listdir(self.upload_dir)
            total_files = len(files)
            total_size = 0
            for file in files:
                file_path = os.path.join(self.upload_dir, file)
                total_size += os.path.getsize(file_path)
            return {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            }
        except Exception as e:
            return {"error": str(e)}

    def cleanup_old_files(self, days_old: int = 30):
        """Clean up files older than specified days"""
        try:
            import time
            current_time = time.time()
            removed_count = 0
            for file in os.listdir(self.upload_dir):
                file_path = os.path.join(self.upload_dir, file)
                file_age = current_time - os.path.getctime(file_path)
                if file_age > (days_old * 24 * 60 * 60):  # Convert days to seconds
                    os.remove(file_path)
                    removed_count += 1
            return {"removed_files": removed_count}
        except Exception as e:
            return {"error": str(e)}