# Metal Math App
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from random import sample # used for sampling questions
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
question_path = os.path.join('static', 'data', 'mc_full_data.json')
covered_questions = set()

def init_xp_tracking():
    if 'xp_total' not in session:
        session['xp_total'] = 0
    if 'unit_xp' not in session:
        session['unit_xp'] = {unit_id: 0 for unit_id in data.keys()}


@app.route('/')
def home():
    init_xp_tracking()
    updated_data = {}
    for unit_id, unit_info in data.items():
        updated_data[unit_id] = {
            "unit": unit_info["unit"],
            "difficulty": unit_info["difficulty"],
            "progress": session['unit_xp'].get(unit_id, 0)
        }
    return render_template('home.html', data=updated_data, xp_total=session['xp_total'])


@app.route('/learn/<unit_id>', methods=['GET'])
def learn(unit_id):
	with open(learn_path, encoding='utf-8') as f:
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
    init_xp_tracking()
    unit = data[unit_id]
    unit_name = unit["unit"]
    xp_progress = session['unit_xp'].get(unit_id, 0)
    return render_template('unit.html', unit_id=unit_id, unit_name=unit_name, xp_progress=xp_progress)


@app.route('/practice/<unit_id>/<mode>', methods=['GET'])
def practice(unit_id, mode):
    unit_name = data[unit_id]['unit']
    with open(question_path, encoding='utf-8') as f:
        all_questions = json.load(f)[unit_id][mode]
        print(all_questions.keys())
    
    # Sample 5 unique questions
    question_batch = sample(list(set(all_questions.keys()) - covered_questions), 5)
    # print(question_batch)
    q_id = question_batch[0]
    question = all_questions[q_id]['problem']
    # print("practice: ", q_id, question)
    # Store in session
    session['practice_data'] = {
        'unit_id': unit_id,
        'mode': mode,
        'unit_name': unit_name,
        'questions': question_batch,
        'all_questions': all_questions,
        'current_index': 0,
        'responses': [],
        'score': 0
    }
    return render_template(
        'practice.html',
        unit_id=unit_id,
        unit_name=unit_name,
        mode=mode,
        question=question,
        questionData=all_questions[q_id],
        progress=0
    )
@app.route('/submit_practice_answer', methods=['POST'])
def submit_practice_answer():
    user_answer = request.form['user-answer']
    data = session['practice_data']
    idx = data['current_index']
    q_id = data['questions'][idx]
    all_questions = data['all_questions']
    print("submit: current question: ", q_id, all_questions[q_id])
    correct_answer = all_questions[q_id]['answer']

    # Track score
    is_correct = str(user_answer).strip() == str(correct_answer).strip()
    if is_correct:
        data['score'] += 1
        
    covered_questions.add(q_id)  # Mark question as covered

    # Save response
    data['responses'].append({
        'question': all_questions[q_id]['problem'],
        'user_answer': user_answer,
        'correct_answer': correct_answer,
        'correct': is_correct
    })

    session['practice_data'] = data  # update

    return jsonify(correct=is_correct, message="Nice!" if is_correct else f"Oops! The correct answer was {correct_answer}")

@app.route('/next_practice')
def next_practice():
    data = session['practice_data']
    question_batch = data['questions']
    data['current_index'] += 1

    if data['current_index'] >= len(question_batch):
        return redirect(url_for('practice_summary'))

    q_id = question_batch[data['current_index']]
    question_data = data['all_questions'][q_id]
    session['practice_data'] = data

    progress = int(100 * data['current_index'] / len(question_batch))

    return render_template(
        'practice.html',
        unit_id=data['unit_id'],
        unit_name=data['unit_name'],
        mode=data['mode'],
        question=question_data['problem'],
        progress=progress,
        questionData=question_data  # <-- Add this line
    )

@app.route('/practice_summary')
def practice_summary():
    init_xp_tracking()
    data_ = session['practice_data']
    score = data_['score']
    unit_id = data_['unit_id']
    mode = data_['mode']

    # XP logic
    xp_earned = 3 if score >= 3 else 1
    unit_xp_gain = xp_earned * 5

    # Update unit XP
    old_unit_xp = session['unit_xp'].get(unit_id, 0)
    session['unit_xp'][unit_id] = min(old_unit_xp + unit_xp_gain, 100)

    # Update total XP
    old_total_xp = session['xp_total']
    session['xp_total'] = min(old_total_xp + unit_xp_gain, 100)

    session.modified = True
    return render_template(
        'practice_summary.html',
        score=score,
        xp=xp_earned,
        unit_id=unit_id,
        mode=mode,
        xp_progress=session['unit_xp'][unit_id],
        xp_total=session['xp_total']
    )



@app.route('/quiz/<unit_id>')
def quiz(unit_id):
    with open(question_path, encoding='utf-8') as f:
        all_questions = json.load(f)[unit_id]['test']  # Use the passed-in unit_id

    if 'quiz_data' not in session or session['quiz_data'].get('unit_id') != unit_id:
        # Sample 5 random questions
        question_batch = sample(list(all_questions.keys()), 5)

        session['quiz_data'] = {
            'unit_id': unit_id,
            'questions': question_batch,
            'all_questions': all_questions,
            'current_index': 0,
            'responses': [],
            'score': 0,
            'quiz_start_time': datetime.utcnow().isoformat(),     # overall quiz start
            'question_start_time': datetime.utcnow().isoformat()  # first question start
        }

    data = session['quiz_data']

    if data['current_index'] >= len(data['questions']):
        return redirect(url_for('quiz_results'))

    q_id = data['questions'][data['current_index']]
    question = data['all_questions'][q_id]['problem']
    progress = int(100 * data['current_index'] / len(data['questions']))
    start_time = datetime.fromisoformat(data['quiz_start_time'])
    elapsed = round((datetime.utcnow() - start_time).total_seconds(), 2)
    time_left = max(0, int(300 - elapsed))

    return render_template(
        'quiz.html',
        unit_id=unit_id,
        question=question,
        progress=progress,
        time_left=time_left
    )



@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    user_answer = request.form['user-answer']
    data = session['quiz_data']
    idx = data['current_index']
    q_id = data['questions'][idx]
    correct_answer = data['all_questions'][q_id]['answer']

    # Use question_start_time to measure time spent on current question
    question_start_time = datetime.fromisoformat(data["question_start_time"])
    time_spent = round((datetime.utcnow() - question_start_time).total_seconds(), 2)

    # Check if correct
    is_correct = str(user_answer).strip() == str(correct_answer).strip()
    if is_correct:
        data['score'] += 1

    # Save user response
    data['responses'].append({
        'id': q_id,
        'question': data['all_questions'][q_id]['problem'],
        'user_answer': user_answer,
        'correct_answer': correct_answer,
        'correct': is_correct,
        'time_spent': time_spent
    })

    session['quiz_data'] = data

    return jsonify(correct=is_correct, message="Nice!" if is_correct else f"Oops! The correct answer was {correct_answer}")


@app.route('/next_quiz')
def next_quiz():
    if 'quiz_data' not in session:
        return redirect(url_for('home'))

    data = session['quiz_data']
    data['current_index'] += 1

    if data['current_index'] >= len(data['questions']):
        return redirect(url_for('quiz_results'))

    # Reset question_start_time for the new question
    data['question_start_time'] = datetime.utcnow().isoformat()

    q_id = data['questions'][data['current_index']]
    question = data['all_questions'][q_id]['problem']
    print("next: ", q_id, question)
    progress = int(100 * data['current_index'] / len(data['questions']))
    
    # Still computing quiz elapsed for total timer
    quiz_start_time = datetime.fromisoformat(data['quiz_start_time'])
    elapsed = round((datetime.utcnow() - quiz_start_time).total_seconds(), 2)
    time_left = max(0, int(300 - elapsed))

    session['quiz_data'] = data
    return render_template(
        'quiz.html',
        unit_id=data['unit_id'],
        question=question,
        progress=progress,
        time_left=time_left
    )

@app.route('/quiz_results')
def quiz_results():
    init_xp_tracking()
    data_ = session['quiz_data']
    score = data_['score']
    unit_id = data_['unit_id']
    quiz_start_time = datetime.fromisoformat(data_['quiz_start_time'])
    total_time = round((datetime.utcnow() - quiz_start_time).total_seconds(), 2)

    xp_earned = 3 if score >= 3 else 1
    unit_xp_gain = xp_earned * 5

    # Update unit XP
    old_unit_xp = session['unit_xp'].get(unit_id, 0)
    session['unit_xp'][unit_id] = min(old_unit_xp + unit_xp_gain, 100)

    # Update total XP
    old_total_xp = session['xp_total']
    session['xp_total'] = min(old_total_xp + unit_xp_gain, 100)

    session.modified = True
    return render_template(
        'quiz_results.html',
        score=score,
        xp=xp_earned,
        unit_id=unit_id,
        xp_progress=session['unit_xp'][unit_id],
        xp_total=session['xp_total'],
        total_time=total_time   # <-- NEW
    )



@app.route('/clear_quiz_session')
def clear_quiz_session(redirect_url='home'):
    # can save data here, perhaps thru pickling so we dont need a DBMS
    session.pop('quiz_data')
    return redirect(url_for('home'))

@staticmethod
def is_question_correct(question_datum, user_response): # takes in an element from question_data, and a user_response dict
    user_answer = user_response['user-answer']
    if not user_answer.isdigit():
        return False
    return int(user_answer) == int(question_datum['answer'])



@app.route('/quiz_review_mistakes')
def quiz_review_mistakes():
    mistakes = []
    quiz_data = session['quiz_data']

    for response in quiz_data['responses']:
        if not response['correct']:
            mistakes.append({
			'user-response': response,
			'problem-data': {
				'id': response['id'],  # <- Add this!
				'problem': response['question'],
				'correct_answer': response['correct_answer'],
                'user_answer': response['user_answer'],
                'time_spent': response['time_spent']
			}
		})

    return render_template('quiz_review_mistakes.html', review_data=mistakes)

@app.route('/quiz_problem_review/<qid>')
def quiz_problem_review(qid):
    if 'quiz_data' not in session:
        return redirect(url_for('home'))  # Safety check

    data = session['quiz_data']
    all_questions = data['all_questions']

    # Look for the specific question ID
    if qid not in all_questions:
        return "Question not found.", 404

    question_data = all_questions[qid]
    gif_url = question_data['solution_gif'][6:]  # Assuming you store path like 'static/data/...'

    return render_template('quiz_problem_review.html', gif_url=gif_url)


@app.route('/summary')
def summary():
	return render_template('summary.html')

if __name__ == '__main__':
    app.secret_key = secrets.token_hex(16)
    app.run(debug=True, port=5001)
