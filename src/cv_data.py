# cv_data.py
import json
import os

def load_cv_data():
    try:
        # Use a relative path to locate cv.json
        current_dir = os.path.dirname(__file__)  # Get the directory of the current file
        cv_path = os.path.join(current_dir, '..', 'data', 'cv.json')  # Go up one level and into the data folder
        with open(cv_path, 'r') as f:
            cv_data = json.load(f)
        print("CV data loaded successfully")
        return cv_data
    except FileNotFoundError:
        print("Error: cv.json not found.")
        return {}