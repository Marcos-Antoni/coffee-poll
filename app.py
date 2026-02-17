import json
import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
DB_FILE = 'votes.json'

# Configuración de zona horaria UTC-6
TZ_OFF = timezone(timedelta(hours=-6))

def get_now():
    return datetime.now(timezone.utc).astimezone(TZ_OFF)

def load_votes():
    now = get_now()
    if not os.path.exists(DB_FILE):
        return {"si": 0, "no": 0, "voters": [], "last_reset": now.isoformat()}
    
    with open(DB_FILE, 'r') as f:
        data = json.load(f)
    
    # Reiniciar si ha pasado más de un día según la hora local (UTC-6)
    last_reset = datetime.fromisoformat(data.get('last_reset', now.isoformat()))
    if now - last_reset > timedelta(days=1):
        data = {"si": 0, "no": 0, "voters": [], "last_reset": now.isoformat()}
        save_votes(data)
    
    return data

def save_votes(votes):
    with open(DB_FILE, 'w') as f:
        json.dump(votes, f)

@app.route('/')
def index():
    votes = load_votes()
    return render_template('index.html', votes=votes)

@app.route('/vote', methods=['POST'])
def vote():
    choice = request.form.get('choice')
    try:
        cups = int(request.form.get('cups', 1))
    except:
        cups = 1
    
    votes = load_votes()
    now = get_now()
    if choice == 'si':
        votes['si'] += cups
        votes['voters'].append({"cups": cups, "choice": choice, "time": now.strftime("%H:%M")})
    elif choice == 'no':
        votes['no'] += 1
        votes['voters'].append({"cups": 0, "choice": choice, "time": now.strftime("%H:%M")})
    
    save_votes(votes)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
