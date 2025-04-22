# Metal Math App

from flask import Flask, render_template, request, jsonify, redirect, session, url_for

import json
import os

import math_data

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/unit')
def unit():
	unit_title = "Addition Basics"
	xp_progress = 36  # Example progress in percentage
	return render_template('unit.html', unit_title=unit_title, xp_progress=xp_progress)

@app.route('/learn')
def learn():
	return render_template('learn.html')

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
