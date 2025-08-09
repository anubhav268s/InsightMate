import os
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

class DataService:
    def __init__(self):
        # Initialize data storage paths
        self.data_dir = settings.DATA_DIRECTORY
        self.user_data_file = settings.USER_DATA_FILE
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        # Initialize user data structure
        self._init_user_data()

    def _init_user_data(self):
        # Initialize user data file if it doesn't exist
        if not os.path.exists(self.user_data_file):
            initial_data = {
                "portfolio_links": [],
                "files": {},
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            self._save_user_data(initial_data)

    def get_user_data(self) -> Dict[str, Any]:
        # Get all user data
        try:
            with open(self.user_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self._init_user_data()
            return self.get_user_data()
        except json.JSONDecodeError:
            # If file is corrupted, reinitialize
            self._init_user_data()
            return self.get_user_data()

    def _save_user_data(self, data: Dict[str, Any]):
        # Save user data to file
        data["updated_at"] = datetime.now().isoformat()
        with open(self.user_data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_portfolio_link(self, link_data: Dict[str, Any], processed_content: str = "") -> str:
        # Add a portfolio link with processed content
        user_data = self.get_user_data()
        link_entry = {
            "id": str(uuid.uuid4()),
            "url": link_data["url"],
            "type": link_data["type"],
            "description": link_data.get("description", ""),
            "content": processed_content,
            "added_at": datetime.now().isoformat()
        }
        user_data["portfolio_links"].append(link_entry)
        self._save_user_data(user_data)
        return link_entry["id"]

    def add_file_data(self, filename: str, processed_content: str):
        # Add processed file data
        user_data = self.get_user_data()
        file_entry = {
            "filename": filename,
            "content": processed_content,
            "file_type": self._get_file_type(filename),
            "uploaded_at": datetime.now().isoformat()
        }
        if "files" not in user_data or not isinstance(user_data["files"], dict):
            user_data["files"] = {}
        user_data["files"][filename] = file_entry
        self._save_user_data(user_data)

    def delete_file(self, filename: str):
        # Delete file data
        user_data = self.get_user_data()
        if filename in user_data.get("files", {}):
            del user_data["files"][filename]
            self._save_user_data(user_data)
            return True
        return False

    def delete_portfolio_link(self, link_id: str):
        # Delete portfolio link by ID
        user_data = self.get_user_data()
        user_data["portfolio_links"] = [
            link for link in user_data.get("portfolio_links", []) if link["id"] != link_id
        ]
        self._save_user_data(user_data)
        return True

    def get_portfolio_links(self) -> List[Dict[str, Any]]:
        # Get all portfolio links
        user_data = self.get_user_data()
        return user_data.get("portfolio_links", [])

    def get_files(self) -> Dict[str, Any]:
        # Get all file data
        user_data = self.get_user_data()
        return user_data.get("files", {})

    def clear_all_data(self):
        # Clear all user data (for testing or reset)
        initial_data = {
            "portfolio_links": [],
            "files": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self._save_user_data(initial_data)

    def get_data_summary(self) -> Dict[str, Any]:
        # Get summary of user data
        user_data = self.get_user_data()
        return {
            "total_portfolio_links": len(user_data.get("portfolio_links", [])),
            "total_files": len(user_data.get("files", {})),
            "portfolio_types": list(set(
                link["type"] for link in user_data.get("portfolio_links", [])
            )),
            "file_types": list(set(
                file_data["file_type"] for file_data in user_data.get("files", {}).values()
            )),
            "created_at": user_data.get("created_at"),
            "updated_at": user_data.get("updated_at")
        }

    def _get_file_type(self, filename: str) -> str:
        # Determine file type from filename
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        type_mapping = {
            "pdf": "pdf",
            "doc": "document",
            "docx": "document",
            "txt": "text",
            "jpg": "image",
            "jpeg": "image",
            "png": "image",
            "gif": "image",
            "csv": "spreadsheet",
            "xlsx": "spreadsheet",
            "xls": "spreadsheet"
        }
        return type_mapping.get(extension, "unknown")

    def backup_data(self, backup_path: str = None) -> str:
        # Create a backup of user data
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.data_dir, f"backup_{timestamp}.json")
        user_data = self.get_user_data()
        with open(backup_path, "w", encoding='utf-8') as f:
            json.dump(user_data, f, indent=2, ensure_ascii=False)
        return backup_path

    def restore_data(self, backup_path: str) -> bool:
        # Restore user data from backup
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            # Validate backup data structure
            required_keys = ["portfolio_links", "files"]
            if all(key in backup_data for key in required_keys):
                self._save_user_data(backup_data)
                return True
            else:
                return False
        except (FileNotFoundError, json.JSONDecodeError):
            return False