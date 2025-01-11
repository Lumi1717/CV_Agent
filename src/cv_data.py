import json

def load_cv_data():
    try:
        with open('/Users/ahlamyusuf/CvBot/data/cv.json', 'r') as f:
            cv_data = json.load(f)
        print("CV data loaded successfully")
        return cv_data
    except FileExistsError:
        print("Error: cv.json not found.")
        return {}
    