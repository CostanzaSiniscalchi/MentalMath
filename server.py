# Metal Math App

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
import math_data

app = Flask(__name__)

data = {"1": {"unit": "Multiplication by 11", "difficulty": "Easy", "progress": 0},
		"2": {"unit": "Square Numbers Ending in 5", "difficulty": "Medium", "progress": 0},
		"3": {"unit": "Midpoint Square Multiplication", "difficulty": "Hard", "progress": 0}
		}
json_path = os.path.join('static', 'data', 'learn', 'learn_units.json')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/learn/<unit_id>', methods=['GET'])
def learn(unit_id):
	with open(json_path) as f:
		tutorial_data = json.load(f)
		steps = tutorial_data.get(unit_id)
		if not steps:
			return "Unit not found", 404
	if unit_id not in data:
		return "Unit not found", 404
	unit_name = data[unit_id]["unit"]
	img_base_url = url_for('static', filename=f'data/learn/{unit_id}/')
	return render_template('learn.html', unit_id=unit_id, unit_name = unit_name, steps=steps, img_base_url=img_base_url)

@app.route('/unit/<unit_id>')
def unit(unit_id):
	unit = data[unit_id]
	unit_name = unit["unit"]
	xp_progress = unit["progress"]
	return render_template('unit.html', unit_id=unit_id, unit_name = unit_name, xp_progress = xp_progress)

@app.route('/practice')
def practice():
	return render_template('practice.html')

@app.route('/quiz')
def quiz():
    question = "What is 11 × 13?"
    options = ["143", "123", "153"]
    progress = 20  # For example, 20% through the quiz
    time_left = 300  # 5 minutes in seconds

    return render_template(
        'quiz.html',  # or 'lightning_round.html'
        question=question,
        options=options,
        progress=progress,
        time_left=time_left
    )

@app.route('/review')
def review():
	return render_template('review_mistakes.html')

@app.route('/summary')
def summary():
	return render_template('summary.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
