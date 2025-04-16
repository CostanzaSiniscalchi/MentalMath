math_problems = [
	{
		"id": 1,
		"question": "What is 2 + 2?",
		"answer": 4,
		"difficulty": "easy",
		"category": ["addition"]
	}
]

def get_math_problems(category=None, difficulty=None):
	if category is None and difficulty is None:
		return math_problems
	else:
		filtered_problems = []
		for problem in math_problems:
			if (category is None or problem["category"] == category) and (difficulty is None or problem["difficulty"] == difficulty):
				filtered_problems.append(problem)
		return filtered_problems
	return math_problems

def get_problem_by_id(problem_id):
	for problem in math_problems:
		if problem["id"] == problem_id:
			return problem
	return None

def search_problems(query):
	results = []
	for problem in math_problems:
		if query.lower() in problem["question"].lower():
			results.append(problem)
	return results