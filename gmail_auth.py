import os
import pickle
import logging
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Configure logging
logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Paths
CREDENTIALS_FILE = 'credentials.json'
GMAIL_TOKEN_PATH = "tokens/token_saher.sharaf68@gmail.com.pickle"

def load_gmail_creds():
    """Load Gmail credentials from pickle file"""
    try:
        if os.path.exists(GMAIL_TOKEN_PATH):
            with open(GMAIL_TOKEN_PATH, "rb") as token:
                creds = pickle.load(token)
            
            # Refresh token if expired
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        # Save refreshed credentials
                        with open(GMAIL_TOKEN_PATH, "wb") as token:
                            pickle.dump(creds, token)
                        logger.info("Gmail credentials refreshed successfully")
                    except Exception as e:
                        logger.error(f"Error refreshing Gmail credentials: {e}")
                        raise
                else:
                    logger.error("Gmail credentials are invalid and cannot be refreshed")
                    raise Exception("Invalid Gmail credentials")
            
            return creds
        else:
            logger.error(f"Gmail token file not found: {GMAIL_TOKEN_PATH}")
            raise FileNotFoundError(f"Gmail token file not found: {GMAIL_TOKEN_PATH}")
            
    except Exception as e:
        logger.error(f"Error loading Gmail credentials: {e}")
        raise

def create_gmail_credentials():
    """Create Gmail credentials (run this once to set up authentication)"""
    try:
        if not os.path.exists(CREDENTIALS_FILE):
            logger.error(f"Credentials file not found: {CREDENTIALS_FILE}")
            print(f"Please download your credentials.json file from Google Cloud Console")
            print(f"and place it in the project root directory")
            return False
        
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        os.makedirs(os.path.dirname(GMAIL_TOKEN_PATH), exist_ok=True)
        with open(GMAIL_TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)
        
        logger.info("Gmail credentials created successfully")
        print(f"Credentials saved to: {GMAIL_TOKEN_PATH}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating Gmail credentials: {e}")
        print(f"Error creating Gmail credentials: {e}")
        return False

def test_gmail_connection():
    """Test Gmail API connection"""
    try:
        creds = load_gmail_creds()
        service = build('gmail', 'v1', credentials=creds)
        
        # Test by checking if credentials are valid for sending emails
        # We only have gmail.send scope, so we can't test getProfile
        if creds.valid:
            logger.info("Gmail credentials are valid and ready for sending emails")
            print("Gmail credentials are valid and ready for sending emails")
            return True
        else:
            logger.error("Gmail credentials are invalid")
            print("Gmail credentials are invalid")
            return False
        
    except Exception as e:
        logger.error(f"Gmail connection test failed: {e}")
        print(f"Gmail connection test failed: {e}")
        return False

def setup_gmail_auth():
    """Setup Gmail authentication interactively"""
    print("Gmail Authentication Setup")
    print("=" * 30)
    
    if os.path.exists(GMAIL_TOKEN_PATH):
        print("Existing Gmail credentials found. Testing connection...")
        if test_gmail_connection():
            print("✅ Gmail is already set up and working!")
            return True
        else:
            print("❌ Existing credentials are not working. Creating new ones...")
    
    print("\nSetting up new Gmail credentials...")
    print("1. Make sure you have downloaded credentials.json from Google Cloud Console")
    print("2. Enable Gmail API in your Google Cloud project")
    print("3. Set up OAuth consent screen")
    
    input("Press Enter when ready to continue...")
    
    if create_gmail_credentials():
        print("✅ Gmail authentication setup completed!")
        return test_gmail_connection()
    else:
        print("❌ Failed to set up Gmail authentication")
        return False

if __name__ == "__main__":
    # Interactive setup
    setup_gmail_auth()
