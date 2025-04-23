import json
import os
import random
math_problems = [
	{'id': 1, 'question': 'What is 11 × 29?', 'answer': 319, 'difficulty': 'test',
	 'category': ['Multiplication by 11']},
	{'id': 2, 'question': 'What is 11 × 38?', 'answer': 418, 'difficulty': 'test',
	 'category': ['Multiplication by 11']},
	{'id': 3, 'question': 'What is 11 × 12?', 'answer': 132, 'difficulty': 'test',
	 'category': ['Multiplication by 11']},
	{'id': 4, 'question': 'What is 11 × 67?', 'answer': 737, 'difficulty': 'test',
	 'category': ['Multiplication by 11']},
	{'id': 5, 'question': 'What is 11 × 145?', 'answer': 1595, 'difficulty': 'test',
	 'category': ['Multiplication by 11']},
	{'id': 6, 'question': 'What is 11 × 21?', 'answer': 231, 'difficulty': 'test',
	 'category': ['Multiplication by 11']},
	{'id': 7, 'question': 'What is 11 × 56?', 'answer': 616, 'difficulty': 'test',
	 'category': ['Multiplication by 11']},
	{'id': 8, 'question': 'What is 11 × 303?', 'answer': 3333, 'difficulty': 'test',
	 'category': ['Multiplication by 11']},
	{'id': 9, 'question': 'What is 11 × 75?', 'answer': 825, 'difficulty': 'test',
	 'category': ['Multiplication by 11']},
	{'id': 10, 'question': 'What is 11 × 121?', 'answer': 1331, 'difficulty': 'test',
	 'category': ['Multiplication by 11']},

{
		"id": 11,
		"question": "What is 2 + 2?",
		"answer": 4,
		"difficulty": "easy",
		"category": ["addition"]
	}
]

# You can load this once globally or on every request
def load_questions():
    with open(os.path.join('data', 'questions.json')) as f:
        return json.load(f)


def load_random_questions(n=5):
    questions = load_questions()
    return random.sample(questions, k=n)


# def get_math_problems(category=None, difficulty=None):
# 	if category is None and difficulty is None:
# 		return math_problems
# 	else:
# 		filtered_problems = []
# 		for problem in math_problems:
# 			if (category is None or problem["category"] == category) and (difficulty is None or problem["difficulty"] == difficulty):
# 				filtered_problems.append(problem)
# 		return filtered_problems
# 	return math_problems

# def get_problem_by_id(problem_id):
# 	for problem in math_problems:
# 		if problem["id"] == problem_id:
# 			return problem
# 	return None

# def search_problems(query):

# 	results = []
# 	for problem in math_problems:
# 		if query.lower() in problem["question"].lower():
# 			results.append(problem)
# 	return results