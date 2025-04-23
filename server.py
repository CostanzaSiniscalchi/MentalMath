# Metal Math App

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from random import sample # used for sampling questions
import secrets # used for session secret key
from datetime import datetime # used for tracking time left on the backend
import json
import os
import math_data

app = Flask(__name__)

data = {"1": {"unit": "Multiplication by 11", "difficulty": "Easy", "progress": 0, "q_path": "static/data/multiply11.json"},
		"2": {"unit": "Square Numbers Ending in 5", "difficulty": "Medium", "progress": 0, "q_path": "static/data/squared5.json"},
		"3": {"unit": "Midpoint Square Multiplication", "difficulty": "Hard", "progress": 0, "q_path": "static/data/midpoint.json"}
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

@app.route('/practice/<unit_id>/<mode>', methods=['GET'])
def practice(unit_id, mode):
    unit_name = data[unit_id]['unit']
    question_path = data[unit_id]['q_path']

    with open(question_path) as f:
        all_questions = json.load(f)[mode]
    
    # Sample 5 unique questions
    question_batch = sample(all_questions, 5)

    # Store in session
    session['practice_data'] = {
        'unit_id': unit_id,
        'mode': mode,
        'unit_name': unit_name,
        'questions': question_batch,
        'current_index': 0,
        'responses': [],
        'score': 0
    }

    question = question_batch[0]['problem']
    return render_template(
        'practice.html',
        unit_id=unit_id,
        unit_name=unit_name,
        mode=mode,
        question=question,
        progress=0
    )
@app.route('/submit_practice_answer', methods=['POST'])
def submit_practice_answer():
    user_answer = request.form['user-answer']
    data = session['practice_data']
    idx = data['current_index']
    correct_answer = data['questions'][idx]['answer']

    # Track score
    is_correct = str(user_answer).strip() == str(correct_answer).strip()
    if is_correct:
        data['score'] += 1

    # Save response
    data['responses'].append({
        'question': data['questions'][idx]['problem'],
        'your_answer': user_answer,
        'correct_answer': correct_answer,
        'correct': is_correct
    })

    session['practice_data'] = data  # update

    return jsonify(correct=is_correct, message="Nice!" if is_correct else f"Oops! The correct answer was {correct_answer}")
@app.route('/next_practice')
def next_practice():
    data = session['practice_data']
    data['current_index'] += 1

    if data['current_index'] >= len(data['questions']):
        return redirect(url_for('practice_summary'))

    session['practice_data'] = data
    question = data['questions'][data['current_index']]['problem']
    progress = int(100 * data['current_index'] / len(data['questions']))

    return render_template(
        'practice.html',
        unit_id=data['unit_id'],
        unit_name=data['unit_name'],
        mode=data['mode'],
        question=question,
        progress=progress
    )


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
