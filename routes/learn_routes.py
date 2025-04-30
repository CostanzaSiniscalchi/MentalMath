from flask import Blueprint, render_template, url_for
import json
from utils.paths import LEARN_PATH, UNIT_DATA

learn_bp = Blueprint('learn', __name__)

@learn_bp.route('/learn/<unit_id>')
def learn(unit_id):
    with open(LEARN_PATH, encoding='utf-8') as f:
        tutorial_data = json.load(f)
        steps = tutorial_data.get(unit_id)

    if not steps or unit_id not in UNIT_DATA:
        return "Unit not found", 404

    unit_name = UNIT_DATA[unit_id]["unit"]
    img_base_url = url_for('static', filename=f'data/learn/{unit_id}/')
    return render_template('learn.html', unit_id=unit_id, unit_name=unit_name, steps=steps, img_base_url=img_base_url)
