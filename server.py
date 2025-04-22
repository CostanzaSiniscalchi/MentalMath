# Metal Math App

from flask import Flask, render_template, request, jsonify, redirect, url_for, session

import secrets # used for session secret key
from datetime import datetime # used for tracking time left on the backend
import json
import os
import math_data

app = Flask(__name__)

data = {"1": {"unit": "Multiplication by 11", "difficulty": "Easy", "progress": 0},
		"2": {"unit": "Square Numbers Ending in 5", "difficulty": "Medium", "progress": 0},
		"3": {"unit": "Midpoint Square Multiplication", "difficulty": "Hard", "progress": 0}
		}
learn_path = os.path.join('static', 'data', 'learn', 'learn_units.json')


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/learn/<unit_id>', methods=['GET'])
def learn(unit_id):
	with open(learn_path) as f:
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
    if len(session) == 0:
        session['start-time'] = datetime.utcnow().isoformat()
        session['unit'] = 1
        session['total'] = 5
        session['quiz-data'] = list(math_data.math_problems[i] for i in range(5))
        session['quiz-responses'] = list()

    # TODO: init session somewhere!

    if len(session['quiz-responses']) == len(session['quiz-data']):
        return redirect(url_for('summary')) # this should actually be results, but we'll use summary as placeholder

    unit = None # this might be vestigial - we'll see if this is removed, keep for now
    question = session['quiz-data'][len(session['quiz-responses'])]['question']
    answer = session['quiz-data'][len(session['quiz-responses'])]['answer']
    progress = int(100 * len(session['quiz-responses'])/max(len(session['quiz-data']), 1))  # For example, 20% through the quiz

    start_time = datetime.fromisoformat(session['start-time'])
    elapsed = (datetime.utcnow() - start_time).total_seconds()
    time_left = max(0, int(300 - elapsed))  # this makes it so refreshing a page doesn't mess up time

    return render_template(
        'quiz.html',  # or 'lightning_round.html',
        unit=unit,
        question=question,
        answer=answer,
        progress=progress,
        time_left=time_left,
    )

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    user_answer = request.form['user-answer']
    responses = session['quiz-responses']
    responses.append(user_answer)
    session['quiz-responses'] = responses

    correct = int(session['quiz-responses'][-1]) == int(session['quiz-data'][len(session['quiz-responses'])-1]['answer'])

    message = 'Great job!'
    if not correct:
        message = 'Good try, we can review this later.'
    return jsonify(correct=correct, message=message)


@app.route('/review')
def review():
	return render_template('review_mistakes.html')

@app.route('/summary')
def summary():
	return render_template('summary.html')

if __name__ == '__main__':
    app.secret_key = secrets.token_hex(16)
    app.run(debug=True, port=5001)
