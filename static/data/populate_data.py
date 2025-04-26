import json
import os


def populate_data(unit1, unit2, unit3):
    # load data drom jsons
    unit_1 = json.loads(unit1)
    unit_2 = json.loads(unit2)
    unit_3 = json.loads(unit3)
    units = [unit_1, unit_2, unit_3]
    id = 0
    data = {}
    # create a dictionary with the data

    for i, unit in enumerate(units):
        for level in unit:
            for question in unit[level]:
                data[str(i)][level][str(id)] = {
                    "problem": question["problem"],
                    "answer": question["answer"],
                    "solution_gif": question["solution_gif"]
                }
                id += 1
    return data

if __name__ == "__main__":
    # Example usage
    unit1_json = 'static/data/multiply11.json'
    unit2_json = 'static/data/squared5.json'
    unit3_json = 'static/data/midpoint.json'
    data = populate_data(unit1_json, unit2_json, unit3_json)
    print(data)