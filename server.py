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
		"3": {"unit": "Midpoint Square Multiplication", "progress": 0},
		"all": {"unit": "Mixed Practice", "progress": 0}
    }
learn_path = os.path.join('static', 'data', 'learn', 'learn_units.json')
question_path = os.path.join('static', 'data', 'full_data.json')
questions_missed = {}

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
    if 'badges' not in session:
        session['badges'] = {unit_id: False for unit_id in data.keys()}  # not earned yet
    if 'perfect_badges' not in session:
        session['perfect_badges'] = {unit_id: False for unit_id in data.keys()}

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

@app.route('/practice/all')
def practice_all():
    update_user_logs("User started Practice All Units mode")
    with open(question_path, encoding='utf-8') as f:
        full_data = json.load(f)

    flat_questions = {}
    for unit_id, modes in full_data.items():
        for mode, questions in modes.items():
            for qid, q in questions.items():
                key = f"{unit_id}|{mode}|{qid}"
                flat_questions[key] = {
                    **q,
                    "unit_id": unit_id,
                    "mode": mode
                }

    selected_keys = sample(list(flat_questions.keys()), min(10, len(flat_questions)))

    session['practice_data'] = {
        'unit_id': 'all',
        'mode': 'mixed',
        'unit_name': 'Mixed Practice',
        'questions': selected_keys,
        'current_index': 0,
        'responses': [],
        'score': 0
    }

    first = flat_questions[selected_keys[0]]
    return render_template(
        'practice.html',
        unit_id='all',
        unit_name='Mixed Practice',
        mode='mixed',
        question=first['problem'],
        questionData=first,
        progress=0
    )


@app.route('/practice/<unit_id>/<mode>', methods=['GET'])
def practice(unit_id, mode):
    unit_name = data[unit_id]['unit']
    update_user_logs(f'User went to practice unit {unit_id} {mode}')
    with open(question_path, encoding='utf-8') as f:
        all_questions = json.load(f)[unit_id][mode]
        #print(all_questions.keys())
    
    # Sample 5 unique questions
    question_batch = sample(list(set(all_questions.keys())), 5)

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
    key = data['questions'][idx]
    if '|' in key:
        unit_id, mode, qid = key.split('|')
        with open(question_path, encoding='utf-8') as f:
            question = json.load(f)[unit_id][mode][qid]
    else:
        qid = key
        question = data['all_questions'][qid]

    correct_answer = question['answer']
    update_user_logs(f'User submitted answer {user_answer} to question {question["problem"]}')
    # Track score
    is_correct = str(user_answer).strip() == str(correct_answer).strip()
    if is_correct:
        data['score'] += 1
        
    # covered_questions.add(qid)  # Mark question as covered

    # Save response
    data['responses'].append({
        'question': question['problem'],
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
    
    key = question_batch[data['current_index']]
    if '|' in key:
        unit_id, mode, qid = key.split('|')
        with open(question_path, encoding='utf-8') as f:
            question_data = json.load(f)[unit_id][mode][qid]
        unit_name = 'Mixed Practice'
    else:
        qid = key
        question_data = data['all_questions'][qid]
        unit_id = data['unit_id']
        mode = data['mode']
        unit_name = data['unit_name']

    session['practice_data'] = data

    progress = int(100 * data['current_index'] / len(question_batch))

    return render_template(
        'practice.html',
        unit_id=unit_id,
        unit_name=unit_name,
        mode=mode,
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

    # Initialize or reset quiz data if:
    # - not already in session
    # - unit has changed
    # - quiz is finished
    reset_quiz = (
        'quiz_data' not in session or
        not session['quiz_data'] or 
        session['quiz_data'].get('unit_id') != unit_id
    )

    if reset_quiz:
        question_batch = sample(list(all_questions.keys()), 5)
        session['quiz_data'] = {
            'unit_id': unit_id,
            'questions': question_batch,
            'all_questions': all_questions,
            'current_index': 0,
            'responses': [],
            'score': 0,
            'quiz_start_time': datetime.utcnow().isoformat(),
            'question_start_time': datetime.utcnow().isoformat()
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
        if q_id in questions_missed:
            del questions_missed[q_id]
    else:
        questions_missed[q_id] = {"problem": data['all_questions'][q_id]['problem'],
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'time_spent': time_spent,
                'solution_gif': data['all_questions'][q_id].get('solution_gif', '')}

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

    session['unit_xp'][unit_id] = min(session['unit_xp'].get(unit_id, 0) + unit_xp_gain, 100)

    # Award mastery badge if XP high enough
    if session['unit_xp'][unit_id] >= 80:
        session['badges'][unit_id] = True

    # Award perfect score badge if score == 5
    if score == 5:
        session['perfect_badges'][unit_id] = True

    session['xp_total'] = min(session['xp_total'] + unit_xp_gain, 100)
    session['unit_scores'][unit_id]['test'] = max(session['unit_scores'][unit_id]['test'], score)
    session.modified = True
    session['quiz_data'] = None

    return render_template(
        'quiz_results.html',
        score=score,
        xp=unit_xp_gain,
        unit_id=unit_id,
        xp_progress=session['unit_xp'][unit_id],
        xp_total=session['xp_total'],
        badges=session['badges'][unit_id],
        perfect=session['perfect_badges'][unit_id],  # NEW
        total_time=total_time
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
    update_user_logs('User went to quiz review mistakes')
    
    # Transform questions_missed into expected format
    review_data = []
    for qid, details in questions_missed.items():
        review_data.append({
            'problem-data': {
                'id': qid,
                'problem': details['problem']
            },
            'user-response': {
                'user_answer': details['user_answer'],
                'correct_answer': details['correct_answer'],
                'time_spent': details['time_spent']
            }
        })

    return render_template('quiz_review_mistakes.html', review_data=review_data)

@app.route('/quiz_problem_review/<qid>')
def quiz_problem_review(qid):
    if qid not in questions_missed:
        update_user_logs(f'User attempted to review quiz problem {qid}, but it was not found')
        return "Question not found.", 404

    question_data = questions_missed[qid]

    # Get relative path to gif (strip 'static/' from beginning)
    gif_path = question_data.get('solution_gif', '')
    gif_url = gif_path[6:] if gif_path.startswith("static/") else gif_path

    update_user_logs(f'User went to quiz problem review for question {question_data["problem"]}')
    return render_template('quiz_problem_review.html', gif_url=gif_url)



@app.route('/summary')
def summary():
    update_user_logs('User went to summary (badges only)')
    init_xp_tracking()
    badges = session.get('badges', {})
    perfect_badges = session.get('perfect_badges', {})
    xp_total = session.get('xp_total', 0)
    return render_template('summary.html', badges=badges, perfect_badges=perfect_badges, xp_total=xp_total)



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
