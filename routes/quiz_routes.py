from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from utils.paths import UNIT_DATA, QUESTION_PATH
from utils.xp_utils import init_xp_tracking
from datetime import datetime
from random import sample
import json

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/quiz/<unit_id>')
def quiz(unit_id):
    with open(QUESTION_PATH, encoding='utf-8') as f:
        all_questions = json.load(f)[unit_id]['test']

    if 'quiz_data' not in session or session['quiz_data'].get('unit_id') != unit_id:
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
        return redirect(url_for('quiz.quiz_results'))

    q_id = data['questions'][data['current_index']]
    question = data['all_questions'][q_id]['problem']
    progress = int(100 * data['current_index'] / len(data['questions']))
    elapsed = round((datetime.utcnow() - datetime.fromisoformat(data['quiz_start_time'])).total_seconds(), 2)
    time_left = max(0, int(300 - elapsed))

    return render_template('quiz.html', unit_id=unit_id, question=question, progress=progress, time_left=time_left)

@quiz_bp.route('/submit_answer', methods=['POST'])
def submit_answer():
    user_answer = request.form['user-answer']
    data = session['quiz_data']
    idx = data['current_index']
    q_id = data['questions'][idx]
    correct_answer = data['all_questions'][q_id]['answer']

    time_spent = round((datetime.utcnow() - datetime.fromisoformat(data["question_start_time"])).total_seconds(), 2)
    is_correct = str(user_answer).strip() == str(correct_answer).strip()
    if is_correct:
        data['score'] += 1

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

@quiz_bp.route('/next_quiz')
def next_quiz():
    if 'quiz_data' not in session:
        return redirect(url_for('home.home'))

    data = session['quiz_data']
    data['current_index'] += 1
    if data['current_index'] >= len(data['questions']):
        return redirect(url_for('quiz.quiz_results'))

    data['question_start_time'] = datetime.utcnow().isoformat()
    q_id = data['questions'][data['current_index']]
    question = data['all_questions'][q_id]['problem']
    progress = int(100 * data['current_index'] / len(data['questions']))
    elapsed = round((datetime.utcnow() - datetime.fromisoformat(data['quiz_start_time'])).total_seconds(), 2)
    time_left = max(0, int(300 - elapsed))

    session['quiz_data'] = data
    return render_template(
        'quiz.html',
        unit_id=data['unit_id'],
        question=question,
        progress=progress,
        time_left=time_left
    )

@quiz_bp.route('/quiz_results')
def quiz_results():
    if 'quiz_data' not in session:
        return redirect(url_for('home.home'))  # or flash a message first

    init_xp_tracking()
    data_ = session['quiz_data']
    score = data_['score']
    unit_id = data_['unit_id']
    total_time = round((datetime.utcnow() - datetime.fromisoformat(data_['quiz_start_time'])).total_seconds(), 2)

    xp_earned = 3 if score >= 3 else 1
    unit_xp_gain = xp_earned * 5

    session['unit_xp'][unit_id] = min(session['unit_xp'][unit_id] + unit_xp_gain, 100)
    session['xp_total'] = min(session['xp_total'] + unit_xp_gain, 100)

    session.modified = True
	
	
	
    return render_template(
        'quiz_results.html',
        score=score,
        xp=xp_earned,
        unit_id=unit_id,
        xp_progress=session['unit_xp'][unit_id],
        xp_total=session['xp_total'],
        total_time=total_time
    )

@quiz_bp.route('/clear_quiz_session')
def clear_quiz_session():
    session.pop('quiz_data', None)
    return redirect(url_for('home.home'))

@quiz_bp.route('/quiz_review_mistakes')
def quiz_review_mistakes():
    if 'quiz_data' not in session:
        # User likely cleared session or accessed this directly
        return redirect(url_for('quiz.quiz_results'))  # or home or another fallback
    
    quiz_data = session['quiz_data']
    mistakes = [
        {
            'user-response': response,
            'problem-data': {
                'id': response['id'],
                'problem': response['question'],
                'correct_answer': response['correct_answer'],
                'user_answer': response['user_answer'],
                'time_spent': response['time_spent']
            }
        }
        for response in quiz_data['responses'] if not response['correct']
    ]

    return render_template('quiz_review_mistakes.html', review_data=mistakes)

@quiz_bp.route('/quiz_problem_review/<qid>')
def quiz_problem_review(qid):
    if 'quiz_data' not in session:
        return redirect(url_for('home.home'))

    all_questions = session['quiz_data']['all_questions']
    if qid not in all_questions:
        return "Question not found.", 404

    gif_url = all_questions[qid]['solution_gif'][6:]  # Strip "static/"
    return render_template('quiz_problem_review.html', gif_url=gif_url)
