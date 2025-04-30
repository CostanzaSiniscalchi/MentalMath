from flask import Blueprint, render_template, session
from utils.xp_utils import init_xp_tracking
from utils.paths import UNIT_DATA

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    init_xp_tracking()
    updated_data = {
        unit_id: {
            "unit": unit_info["unit"],
            "difficulty": unit_info["difficulty"],
            "progress": session['unit_xp'].get(unit_id, 0)
        }
        for unit_id, unit_info in UNIT_DATA.items()
    }
    return render_template('home.html', data=updated_data, xp_total=session['xp_total'])

@home_bp.route('/summary')
def summary():
    return render_template('summary.html')
