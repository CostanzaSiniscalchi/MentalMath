import os

UNIT_DATA = {
    "1": {"unit": "Multiplication by 11", "difficulty": "Easy", "progress": 0},
    "2": {"unit": "Square Numbers Ending in 5", "difficulty": "Medium", "progress": 0},
    "3": {"unit": "Midpoint Square Multiplication", "difficulty": "Hard", "progress": 0}
}

LEARN_PATH = os.path.join('static', 'data', 'learn', 'learn_units.json')
QUESTION_PATH = os.path.join('static', 'data', 'full_data.json')
