import json
import random
from copy import deepcopy

# Simulating the JSON structure by loading it from a string (since user pasted it)
with open("full_data.json", "r") as f:
    data = json.load(f)

def generate_choices(correct_answer):
    correct = correct_answer
    choices = {correct}
    while len(choices) < 4:
        perturbation = random.choice([-20, -10, -1, 1, 10, 20])
        candidate = correct + perturbation
        if candidate >= 0:
            choices.add(candidate)
    choices = list(choices)
    random.shuffle(choices)
    return choices

# Create a new structure with corrected incremental keys
new_data = deepcopy(data)
for unit_key, unit in data.items():
    for level_key, level in unit.items():
        if level_key == 'easy' or level_key == 'medium':
            existing_items = list(level.items())
            max_key = max(map(int, level.keys())) if level else -1
            for old_key, entry in existing_items:
                if entry.get("type") == "input":
                    max_key += 1
                    mc_entry = deepcopy(entry)
                    mc_entry["type"] = "mc"
                    mc_entry["choices"] = generate_choices(entry["answer"])
                    new_data[unit_key][level_key][str(max_key)] = mc_entry

# Save the updated version
with open("mc_full_data.json", "w") as f:
    json.dump(new_data, f, indent=2)
