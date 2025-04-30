from flask import Blueprint, render_template, session, request, jsonify, redirect, url_for
from utils.paths import UNIT_DATA, QUESTION_PATH
from utils.xp_utils import init_xp_tracking
from random import sample
import json

practice_bp = Blueprint('practice', __name__)

covered_questions = set()

@practice_bp.route('/unit/<unit_id>')
def unit(unit_id):
    init_xp_tracking()
    unit = UNIT_DATA[unit_id]
    unit_name = unit["unit"]
    xp_progress = session['unit_xp'].get(unit_id, 0)
    return render_template('unit.html', unit_id=unit_id, unit_name=unit_name, xp_progress=xp_progress)

@practice_bp.route('/practice/<unit_id>/<mode>')
def practice(unit_id, mode):
    unit_name = UNIT_DATA[unit_id]['unit']
    with open(QUESTION_PATH, encoding='utf-8') as f:
        all_questions = json.load(f)[unit_id][mode]

    question_batch = sample(list(set(all_questions.keys()) - covered_questions), 5)
    q_id = question_batch[0]
    question = all_questions[q_id]['problem']

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

@practice_bp.route('/submit_practice_answer', methods=['POST'])
def submit_practice_answer():
    user_answer = request.form['user-answer']
    data = session['practice_data']
    idx = data['current_index']
    q_id = data['questions'][idx]
    all_questions = data['all_questions']
    correct_answer = all_questions[q_id]['answer']

    is_correct = str(user_answer).strip() == str(correct_answer).strip()
    if is_correct:
        data['score'] += 1
    covered_questions.add(q_id)

    data['responses'].append({
        'question': all_questions[q_id]['problem'],
        'user_answer': user_answer,
        'correct_answer': correct_answer,
        'correct': is_correct
    })

    session['practice_data'] = data
    return jsonify(correct=is_correct, message="Nice!" if is_correct else f"Oops! The correct answer was {correct_answer}")

@practice_bp.route('/next_practice')
def next_practice():
    data = session['practice_data']
    data['current_index'] += 1
    if data['current_index'] >= len(data['questions']):
        return redirect(url_for('practice.practice_summary'))

    q_id = data['questions'][data['current_index']]
    session['practice_data'] = data
    question = data['all_questions'][q_id]['problem']
    progress = int(100 * data['current_index'] / len(data['questions']))

    return render_template(
        'practice.html',
        unit_id=data['unit_id'],
        unit_name=data['unit_name'],
        mode=data['mode'],
        question=question,
        progress=progress
    )

@practice_bp.route('/practice_summary')
def practice_summary():
    init_xp_tracking()
    data_ = session['practice_data']
    score = data_['score']
    unit_id = data_['unit_id']
    mode = data_['mode']

    xp_earned = 3 if score >= 3 else 1
    unit_xp_gain = xp_earned * 5
    session['unit_xp'][unit_id] = min(session['unit_xp'][unit_id] + unit_xp_gain, 100)
    session['xp_total'] = min(session['xp_total'] + unit_xp_gain, 100)

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