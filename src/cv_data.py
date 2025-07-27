# cv_data.py
import json
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_cv_data():
    """
    Load CV data from the JSON file
    
    Returns:
        dict: CV data if successful, empty dict if failed
    """
    try:
        # Use a relative path to locate cv.json
        current_dir = os.path.dirname(__file__)  # Get the directory of the current file
        cv_path = os.path.join(current_dir, '..', 'data', 'cv.json')  # Go up one level and into the data folder
        
        # Convert to absolute path for better error reporting
        cv_path = os.path.abspath(cv_path)
        
        if not os.path.exists(cv_path):
            logger.error(f"CV file not found at path: {cv_path}")
            return {}
        
        with open(cv_path, 'r', encoding='utf-8') as f:
            cv_data = json.load(f)
        
        logger.info("CV data loaded successfully")
        return cv_data
        
    except FileNotFoundError:
        logger.error("Error: cv.json not found.")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error: Invalid JSON format in cv.json - {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"Error loading CV data: {str(e)}")
        return {}