# # google_sync.py
# import os
# from google.oauth2.service_account import Credentials
# import gspread
# from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound, APIError
# from typing import List, Dict, Any

# SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# def get_gspread_client() -> gspread.client.Client:
#     """Initializes and returns an authorized gspread client."""
#     sa_path = os.getenv("GOOGLE_SA_JSON_PATH")
    
#     if not sa_path:
#         raise EnvironmentError("GOOGLE_SA_JSON_PATH environment variable is missing.")

#     try:
#         if not os.path.exists(sa_path):
#             raise FileNotFoundError(f"Service Account file not found at path: {sa_path}")
            
#         creds = Credentials.from_service_account_file(sa_path, scopes=SCOPES)
#         return gspread.authorize(creds)
#     except FileNotFoundError as e:
#         raise EnvironmentError(f"Critical Error: Service Account file access failed. {e}")
#     except Exception as e:
#         raise EnvironmentError(f"Failed to authorize Google Sheets client. Error: {e}")

# def read_sheet_values(spreadsheet_id: str, sheet_name: str = "Sheet1") -> List[Dict[str, Any]]:
#     """Reads all records from a specified Google Sheet and Worksheet."""
#     try:
#         client = get_gspread_client()
#         sh = client.open_by_key(spreadsheet_id)
#         worksheet = sh.worksheet(sheet_name)
        
#         return worksheet.get_all_records()
        
#     except SpreadsheetNotFound:
#         raise ValueError(f"Spreadsheet not found for ID: {spreadsheet_id}. Check sharing settings.")
#     except WorksheetNotFound:
#         raise ValueError(f"Worksheet '{sheet_name}' not found in spreadsheet.")
#     except APIError as e:
#         raise RuntimeError(f"Google Sheets API Error: {e}")
#     except Exception as e:
#         raise RuntimeError(f"An unexpected error occurred during sheet read: {e}")



# google_sync.py
import os
import json
from google.oauth2.service_account import Credentials
import gspread
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound, APIError
from typing import List, Dict, Any

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

def get_gspread_client() -> gspread.client.Client:
    """
    Initializes and returns an authorized gspread client.
    Supports both local file-based credentials and environment-based JSON (for Render).
    """
    creds = None

    try:
        # ✅ 1. First try environment variable (Render deployment)
        google_creds_json = os.getenv("GOOGLE_CREDS_JSON")

        if google_creds_json:
            try:
                creds_dict = json.loads(google_creds_json)
                creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
                return gspread.authorize(creds)
            except json.JSONDecodeError:
                raise EnvironmentError("Invalid GOOGLE_CREDS_JSON format — must be valid JSON.")

        # ✅ 2. Fallback: Local file-based credentials (for local dev)
        sa_path = os.getenv("GOOGLE_SA_JSON_PATH", "google_creds.json")

        if not os.path.exists(sa_path):
            raise FileNotFoundError(f"Service Account file not found at path: {sa_path}")

        creds = Credentials.from_service_account_file(sa_path, scopes=SCOPES)
        return gspread.authorize(creds)

    except FileNotFoundError as e:
        raise EnvironmentError(f"Critical Error: Service Account file access failed. {e}")
    except Exception as e:
        raise EnvironmentError(f"Failed to authorize Google Sheets client. Error: {e}")



def read_sheet_values(spreadsheet_id: str, sheet_name: str = "Sheet1") -> List[Dict[str, Any]]:
    """
    Reads all records from a specified Google Sheet and Worksheet.
    """
    try:
        client = get_gspread_client()
        sh = client.open_by_key(spreadsheet_id)
        worksheet = sh.worksheet(sheet_name)
        return worksheet.get_all_records()

    except SpreadsheetNotFound:
        raise ValueError(f"Spreadsheet not found for ID: {spreadsheet_id}. Check sharing settings.")
    except WorksheetNotFound:
        raise ValueError(f"Worksheet '{sheet_name}' not found in spreadsheet.")
    except APIError as e:
        raise RuntimeError(f"Google Sheets API Error: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred during sheet read: {e}")
