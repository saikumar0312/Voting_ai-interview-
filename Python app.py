## Directory: live-polling-api

# requirements.txt
Flask==3.0.3
Flask-SQLAlchemy==3.1.1

# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poll_str_id = db.Column(db.String(50), unique=True, nullable=False)
    question = db.Column(db.String(255), nullable=False)
    options = db.relationship('PollOption', backref='poll', cascade="all, delete-orphan")

class PollOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    option_str_id = db.Column(db.String(50), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    vote_count = db.Column(db.Integer, default=0)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)

# app.py
from flask import Flask, request, jsonify
from models import db, Poll, PollOption

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/polls', methods=['POST'])
def create_poll():
    data = request.get_json()
    poll_str_id = data['poll_str_id']
    question = data['question']
    options = data['options']

    if Poll.query.filter_by(poll_str_id=poll_str_id).first():
        return jsonify({"error": "Poll ID already exists"}), 400

    poll = Poll(poll_str_id=poll_str_id, question=question)
    db.session.add(poll)
    db.session.flush()

    for opt in options:
        option = PollOption(
            option_str_id=opt['option_str_id'],
            text=opt['text'],
            poll=poll
        )
        db.session.add(option)

    db.session.commit()

    return jsonify({
        "poll_id": poll.poll_str_id,
        "question": poll.question,
        "options": [{"option_str_id": o.option_str_id, "text": o.text, "vote_count": o.vote_count} for o in poll.options]
    }), 201

@app.route('/polls/<poll_str_id>/vote', methods=['POST'])
def vote(poll_str_id):
    data = request.get_json()
    option_str_id = data['option_str_id']

    poll = Poll.query.filter_by(poll_str_id=poll_str_id).first()
    if not poll:
        return jsonify({"error": "Poll not found"}), 404

    option = PollOption.query.filter_by(poll_id=poll.id, option_str_id=option_str_id).first()
    if not option:
        return jsonify({"error": "Option not found"}), 404

    option.vote_count += 1
    db.session.commit()

    return jsonify({"status": "vote_counted", "option": option.option_str_id, "vote_count": option.vote_count})

@app.route('/polls/<poll_str_id>/results', methods=['GET'])
def results(poll_str_id):
    poll = Poll.query.filter_by(poll_str_id=poll_str_id).first()
    if not poll:
        return jsonify({"error": "Poll not found"}), 404

    return jsonify({
        "poll_id": poll.poll_str_id,
        "question": poll.question,
        "results": [{"option_str_id": o.option_str_id, "text": o.text, "vote_count": o.vote_count} for o in poll.options]
    })

if __name__ == '__main__':
    app.run(debug=True)

# README.md
# Live Polling API (Flask)

## Features
- Create polls with options
- Vote on polls
- Retrieve poll results

## Setup
```bash
git clone <repo-url>
cd live-polling-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
## API Endpoints
### Create Poll
POST /polls
```json
{
  "poll_str_id": "fav_color_poll",
  "question": "What is your favorite color?",
  "options": [
    {"option_str_id": "red", "text": "Red"},
    {"option_str_id": "blue", "text": "Blue"}
  ]
}
```

### Vote
POST /polls/fav_color_poll/vote
```json
{ "option_str_id": "red" }
```

### Get Results
GET /polls/fav_color_poll/results


I’ve generated the complete code for your Live Polling Management API using Flask, SQLAlchemy, and SQLite. You can now push it to GitHub. Let me know if you need a GitHub commit message template or guidance on structuring your repository!
