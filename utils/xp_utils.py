from flask import session
from utils.paths import UNIT_DATA

def init_xp_tracking():
    if 'xp_total' not in session:
        session['xp_total'] = 0
    if 'unit_xp' not in session:
        session['unit_xp'] = {unit_id: 0 for unit_id in UNIT_DATA.keys()}
