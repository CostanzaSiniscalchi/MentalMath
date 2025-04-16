# Metal Math App

from flask import Flask, render_template, request, jsonify, redirect, url_for

import math_data

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/learn')
def learn():
	return render_template('learn.html')

@app.route('/practice')
def practice():
	return render_template('practice.html')

@app.route('/quiz')
def quiz():
	return render_template('quiz.html')

@app.route('/review')
def review():
	return render_template('review_mistakes.html')

@app.route('/summary')
def summary():
	return render_template('summary.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
