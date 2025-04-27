import json
import os
from collections import defaultdict

def populate_data(units):
    id = 0
    data = {
        "1": {"easy": defaultdict(dict), "medium": defaultdict(dict), "hard": defaultdict(dict), "test": defaultdict(dict)},
        "2": {"easy": defaultdict(dict), "medium": defaultdict(dict), "hard": defaultdict(dict), "test": defaultdict(dict)},
        "3": {"easy": defaultdict(dict), "medium": defaultdict(dict), "hard": defaultdict(dict), "test": defaultdict(dict)}
    }

    for i, unit in enumerate(units):
        for level in unit:
            for question in unit[level]:
                data[str(i+1)][level][str(id)] = {
                    "problem": question["problem"],
                    "answer": question["answer"],
                    "solution_gif": question["solution_gif"]
                }
                id += 1
    return data

if __name__ == "__main__":
    # Example usage
    unit1_json = 'multiply11.json'
    unit2_json = 'square5.json'
    unit3_json = 'midpoint_problems.json'
    
    units = []
    for unit in [unit1_json, unit2_json, unit3_json]:
        with open(unit, encoding='utf-8') as f:
            units.append(json.load(f))

    data = populate_data(units)
    
    # Save to JSON file
    output_path = 'full_data.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Data successfully written to {output_path}")
