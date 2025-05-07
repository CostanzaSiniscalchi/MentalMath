# Metal Math App
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from random import sample # used for sampling questions
import secrets # used for session secret key
from datetime import datetime # used for tracking time left on the backend
import json
import os
import math_data

app = Flask(__name__)

data = {"1": {"unit": "Multiplication by 11",  "progress": 0},
		"2": {"unit": "Square Numbers Ending in 5",  "progress": 0},
		"3": {"unit": "Midpoint Square Multiplication", "progress": 0}
		}
learn_path = os.path.join('static', 'data', 'learn', 'learn_units.json')
question_path = os.path.join('static', 'data', 'full_data.json')
covered_questions = set()

def init_xp_tracking():
    if 'unit_scores' not in session:
        session['unit_scores'] = {
            unit_id: {mode: 0 for mode in ['tutorial', 'easy', 'medium', 'hard', 'test']}
            for unit_id in data.keys()
        }
    if 'unit_xp' not in session:
        session['unit_xp'] = {unit_id: 0 for unit_id in data.keys()}
    if 'xp_total' not in session:
        session['xp_total'] = 0

def update_user_logs(tracking_tag):
    if 'user_logs' not in session:
        session['user_logs'] = list()
    temp = session['user_logs']

    timestamp = datetime.utcnow().isoformat()
    formatted = datetime.fromisoformat(timestamp).strftime("%H:%M:%S")

    temp.append((tracking_tag, formatted))
    session['user_logs'] = temp
    print(session['user_logs'][-1])

@app.route('/')
def home():
    init_xp_tracking()
    xp = session['unit_xp']
    updated_data = {}
    update_user_logs('Home')
    for unit_id, unit_info in data.items():
        updated_data[unit_id] = {
            "unit": unit_info["unit"],
            "progress": xp.get(unit_id, 0)
        }
    
    # Define unlocks based on previous unit XP
    unlock_requirements = {"2": ("1", 30), "3": ("2", 30)}
    locked_units = set()
    for unit_id, (prev_unit, min_xp) in unlock_requirements.items():
        if xp.get(prev_unit, 0) < min_xp:
            locked_units.add(unit_id)

    return render_template('home.html', data=updated_data, xp_total=session['xp_total'], unit_xp=session['unit_xp'])


@app.route('/learn/<unit_id>', methods=['GET'])
def learn(unit_id):
    with open(learn_path, encoding='utf-8') as f:
        tutorial_data = json.load(f)
        steps = tutorial_data.get(unit_id)
        if not steps:
            update_user_logs(f'User attempted to visit Learn unit {unit_id}, but it was not found')
            return "Unit not found", 404
    if unit_id not in data:
        update_user_logs(f'User attempted to visit Learn unit {unit_id}, but it was not found')
        return "Unit not found", 404
    unit_name = data[unit_id]["unit"]
    img_base_url = url_for('static', filename=f'data/learn/{unit_id}/')
    update_user_logs(f'Learn unit {unit_id}')
    return render_template('learn.html', unit_id=unit_id, unit_name = unit_name, steps=steps, img_base_url=img_base_url)

@app.route('/complete_tutorial_and_redirect/<unit_id>')
def complete_tutorial_and_redirect(unit_id):
    init_xp_tracking()
    if unit_id not in session['unit_scores']:
        session['unit_scores'][unit_id] = {mode: 0 for mode in ['tutorial', 'easy', 'medium', 'hard', 'test']}
    
    # Mark tutorial as complete (score of at least 1)
    session['unit_scores'][unit_id]['tutorial'] = max(session['unit_scores'][unit_id]['tutorial'], 1)
    update_user_logs(f'User completed tutorial for unit {unit_id}')
    session.modified = True

    return redirect(url_for('practice', unit_id=unit_id, mode='easy'))

@app.route('/unit/<unit_id>')
def unit(unit_id):
    init_xp_tracking()
    unit = data[unit_id]
    unit_name = unit["unit"]
    xp_progress = session['unit_xp'].get(unit_id, 0)
    scores = session['unit_scores'][unit_id]
    update_user_logs(f'User went to unit {unit_id}')
    return render_template('unit.html', unit_id=unit_id, unit_name=unit_name, xp_progress=xp_progress, scores = scores)


@app.route('/practice/<unit_id>/<mode>', methods=['GET'])
def practice(unit_id, mode):
    unit_name = data[unit_id]['unit']
    update_user_logs(f'User went to practice unit {unit_id} {mode}')
    with open(question_path, encoding='utf-8') as f:
        all_questions = json.load(f)[unit_id][mode]
        #print(all_questions.keys())
    
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
    update_user_logs(f'User submitted answer {user_answer} to question {all_questions[q_id]["problem"]}')
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
    update_user_logs('User went to next_practice')
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
        questionData=question_data
    )

@app.route('/practice_summary')
def practice_summary():
    update_user_logs('User went to practice summary')
    if 'unit_scores' not in session:
        init_xp_tracking()

    data_ = session['practice_data']
    unit_id = data_['unit_id']
    mode = data_['mode']
    score = data_['score']

    # XP logic
    xp_earned = 3 if score >= 3 else 1
    unit_xp_gain = xp_earned * 5

    # Update unit XP
    old_unit_xp = session['unit_xp'].get(unit_id, 0)
    session['unit_xp'][unit_id] = min(old_unit_xp + unit_xp_gain, 100)

    # Update total XP
    old_total_xp = session['xp_total']
    session['xp_total'] = min(old_total_xp + unit_xp_gain, 100)
    # Update best score if higher
    session['unit_scores'][unit_id][mode] = max(session['unit_scores'][unit_id].get(mode, 0), score)

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
    update_user_logs(f'User went to quiz unit {unit_id}')
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

    if time_left <= 0:
        TLE_populate_responses()
        return redirect(url_for('summary'))

    return render_template(
        'quiz.html',
        unit_id=unit_id,
        question=question,
        progress=progress,
        time_left=time_left
    )



@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    data = session['quiz_data']
    start_time = datetime.fromisoformat(data['quiz_start_time'])
    elapsed = round((datetime.utcnow() - start_time).total_seconds(), 2)
    if elapsed > 300:  # time limit exceeded; null out all inputs
        TLE_populate_responses()
        return jsonify({'redirect': url_for('summary')})


    user_answer = request.form['user-answer']
    data = session['quiz_data']
    idx = data['current_index']
    q_id = data['questions'][idx]
    correct_answer = data['all_questions'][q_id]['answer']

    # Use question_start_time to measure time spent on current question
    question_start_time = datetime.fromisoformat(data["question_start_time"])
    time_spent = round((datetime.utcnow() - question_start_time).total_seconds(), 2)
    update_user_logs(f'User submitted answer {user_answer}')
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
        update_user_logs('User attempted to access quiz data, redirected to Home')
        return redirect(url_for('home'))

    data = session['quiz_data']
    data['current_index'] += 1

    if data['current_index'] >= len(data['questions']):
        update_user_logs('User attempted to access quiz data, redirected to quiz results')
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

    if time_left <= 0:
        TLE_populate_responses()
        return redirect(url_for('summary'))

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
    update_user_logs('User went to quiz results')
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

    session['unit_scores'][unit_id]['test'] = max(session['unit_scores'][unit_id]['test'], score)
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
    update_user_logs('Quiz session data cleared')
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
    if 'quiz_data' not in session:
        update_user_logs('User attempted to access quiz review mistakes, but quiz_data was not found in session, redirected to Home')
        return redirect(url_for('home'))


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
    update_user_logs('User went to quiz review mistakes')
    return render_template('quiz_review_mistakes.html', review_data=mistakes)

@app.route('/quiz_problem_review/<qid>')
def quiz_problem_review(qid):
    if 'quiz_data' not in session:
        update_user_logs('User attempted to visit quiz problem review, but no quiz data was found in session, so was redirected home')
        return redirect(url_for('home'))  # Safety check

    data = session['quiz_data']
    all_questions = data['all_questions']

    # Look for the specific question ID
    if qid not in all_questions:
        update_user_logs(f'User attempted to visit quiz problem review, but question with qid={qid} was not found, so was redirected home')
        return "Question not found.", 404

    question_data = all_questions[qid]
    gif_url = question_data['solution_gif'][6:]  # Assuming you store path like 'static/data/...'
    update_user_logs(f'User went to quiz problem review for question {question_data["problem"]}')
    return render_template('quiz_problem_review.html', gif_url=gif_url)


@app.route('/summary')
def summary():
    update_user_logs('User went to summary')
    return render_template('summary.html')

@app.route('/user-logs')
def user_logs():
    update_user_logs(f'User visited user logs')
    return render_template('logs.html', user_logs=session['user_logs'])

def TLE_populate_responses():
    data = session['quiz_data']
    idx = data['current_index']
    while data['current_index'] < len(data['questions']):
        q_id = data['questions'][idx]
        correct_answer = data['all_questions'][q_id]['answer']
        data['responses'].append({
            'id': q_id,
            'question': data['all_questions'][q_id]['problem'],
            'user_answer': 'N/A',
            'correct_answer': correct_answer,
            'correct': False,
            'time_spent': 'Time limit exceeded'
        })
        data['current_index'] += 1
        idx = data['current_index']
        session['quiz_data'] = data

if __name__ == '__main__':
    app.secret_key = secrets.token_hex(16)
    app.run(debug=True, port=5001)
