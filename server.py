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
question_path = os.path.join('static', 'data', 'full_data.json')
covered_questions = set()

@app.route('/')
def home():
    return render_template('home.html')

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
	unit = data[unit_id]
	unit_name = unit["unit"]
	xp_progress = unit["progress"]
	return render_template('unit.html', unit_id=unit_id, unit_name = unit_name, xp_progress = xp_progress)

@app.route('/practice/<unit_id>/<mode>', methods=['GET'])
def practice(unit_id, mode):
    unit_name = data[unit_id]['unit']
    with open(question_path, encoding='utf-8') as f:
        all_questions = json.load(f)[unit_id][mode]
        print(all_questions.keys())
    
    # Sample 5 unique questions
    question_batch = sample(list(set(all_questions.keys()) - covered_questions), 5)
    print(question_batch)
    q_id = question_batch[0]
    question = all_questions[q_id]['problem']
    print("practice: ", q_id, question)
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

    # Save response
    data['responses'].append({
        'question': all_questions[q_id]['problem'],
        'your_answer': user_answer,
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
        # End of questions, redirect to summary
        return redirect(url_for('practice_summary'))
	
    q_id = question_batch[data['current_index']]
    session['practice_data'] = data
    question = data['all_questions'][q_id]['problem']
    print("next: ", q_id, question)
    progress = int(100 * data['current_index'] / len(question_batch))
    
    return render_template(
        'practice.html',
        unit_id=data['unit_id'],
        unit_name=data['unit_name'],
        mode=data['mode'],
        question=question,
        progress=progress
    )

@app.route('/practice_summary')
def practice_summary():
    data = session['practice_data']
    score = data['score']
    unit_id = data['unit_id']
    mode = data['mode']
    xp = 3 if score >= 3 else 1 # TODO: refreshing causing continuous addition of XP
    data_dict = data  # optionally store review info

    # update XP progress for that unit
    data[unit_id] = data.get(unit_id, {})
    data[unit_id]['progress'] = min(data[unit_id].get('progress', 0) + xp * 5, 100)

    session.modified = True
    return render_template(
        'practice_summary.html',
        score=score,
        xp=xp,
        unit_id=unit_id,
        mode=mode,
        xp_progress=data[unit_id]['progress']
    )


@app.route('/quiz')
def quiz():
    question_path = data['1']['q_path']
    with open(question_path, encoding='utf-8') as f:
        all_questions = json.load(f)['test']
        print(all_questions)
        if not 'quiz-data' in session:
            quiz_data = {
                'start-time': datetime.utcnow().isoformat(),
                'unit-id': 1, # TODO: implement unit selection
                'question-data': sample(all_questions, 5),
                'quiz-responses': list()
            }
            session['quiz-data']= quiz_data

    quiz_data = session['quiz-data']
    # TODO: init session somewhere!

    if len(quiz_data['quiz-responses']) == len(quiz_data['question-data']):
        return redirect(url_for('quiz_results')) # this should actually be results, but we'll use summary as placeholder

    unit = None # this might be vestigial - we'll see if this is removed, keep for now
    question = quiz_data['question-data'][len(quiz_data['quiz-responses'])]['problem']
    answer = quiz_data['question-data'][len(quiz_data['quiz-responses'])]['answer']
    progress = int(100 * len(quiz_data['quiz-responses'])/max(len(quiz_data['question-data']), 1))  # For example, 20% through the quiz

    start_time = datetime.fromisoformat(quiz_data['start-time'])
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
    quiz_data = session['quiz-data']
    user_data = {'user-answer': user_answer, 'time-answered': datetime.utcnow().isoformat()}
    quiz_data['quiz-responses'].append(user_data)
    session['quiz-data'] = quiz_data

    curr_question = quiz_data['question-data'][len(quiz_data['quiz-responses'])-1]
    correct = is_question_correct(curr_question, user_data)

    message = 'Great job!'
    if not correct:
        message = 'Good try, we can review this later.'
    return jsonify(correct=correct, message=message)

@app.route('/quiz_results')
def quiz_results():
    data = session['quiz-data']
    score = 0

    for idx, user_response in enumerate(data['quiz-responses']):
        score += is_question_correct(data['question-data'][idx], user_response)
    unit_id = data['unit-id']
    #mode = data['mode']
    xp = 3 if score >= 3 else 1 # TODO: refreshing causing continuous addition of XP
    data_dict = data  # optionally store review info

    # update XP progress for that unit
    data[unit_id] = data.get(unit_id, {}) 
    data[unit_id]['progress'] = min(data[unit_id].get('progress', 0) + xp * 5, 100)

    #TODO: delete? #session.modified = True
    #session.modified = True
    return render_template(
        'quiz_results.html',
        score=score,
        xp=xp,
        unit_id=unit_id,
        xp_progress=data[unit_id]['progress']
    )

@app.route('/clear_quiz_session')
def clear_quiz_session(redirect_url='home'):
    # can save data here, perhaps thru pickling so we dont need a DBMS
    session.pop('quiz-data')
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
    quiz_data = session['quiz-data']

    for idx, response in enumerate(quiz_data['quiz-responses']):
        if not is_question_correct(quiz_data['question-data'][idx], response):
            mistakes.append({'user-response': response, 'problem-data': quiz_data['question-data'][idx]})
    return render_template('quiz_review_mistakes.html', review_data=mistakes)

@app.route('/quiz_problem_review/<qid>')
def quiz_problem_review(qid):
    all_questions = None
    question_path = data['1']['q_path']
    with open(question_path, encoding='utf-8') as f:
        all_questions = json.load(f)['test']
    question_data = None
    for q in all_questions:
        if str(q['id']) == qid:
            question_data = q
            break
    print(question_data)
    return render_template('quiz_problem_review.html', gif_url=question_data['solution_gif'][6:])

@app.route('/summary')
def summary():
	return render_template('summary.html')

if __name__ == '__main__':
    app.secret_key = secrets.token_hex(16)
    app.run(debug=True, port=5001)
