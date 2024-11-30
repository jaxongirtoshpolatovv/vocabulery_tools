from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vocabulary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    english = db.Column(db.String(100), nullable=False)
    uzbek = db.Column(db.String(100), nullable=False)
    example = db.Column(db.String(200))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    mastered = db.Column(db.Boolean, default=False)
    box_number = db.Column(db.Integer, default=1)
    next_review = db.Column(db.DateTime, default=datetime.utcnow)
    correct_count = db.Column(db.Integer, default=0)
    incorrect_count = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'english': self.english,
            'uzbek': self.uzbek,
            'example': self.example,
            'mastered': self.mastered,
            'box_number': self.box_number,
            'correct_count': self.correct_count,
            'incorrect_count': self.incorrect_count,
            'progress': self.get_progress()
        }
    
    def get_progress(self):
        total = self.correct_count + self.incorrect_count
        if total == 0:
            return 0
        return int((self.correct_count / total) * 100)

    def update_box(self, is_correct):
        if is_correct:
            self.correct_count += 1
            if self.box_number < 5:
                self.box_number += 1
        else:
            self.incorrect_count += 1
            if self.box_number > 1:
                self.box_number = 1
        
        delays = {
            1: timedelta(hours=4),
            2: timedelta(days=1),
            3: timedelta(days=3),
            4: timedelta(days=7),
            5: timedelta(days=14)
        }
        self.next_review = datetime.utcnow() + delays[self.box_number]
        
        if self.box_number == 5 and self.get_progress() >= 90:
            self.mastered = True

with app.app_context():
    db.drop_all()  # Eski bazani o'chirish
    db.create_all()  # Yangi bazani yaratish

@app.route('/')
def index():
    words = Word.query.order_by(Word.date_added.desc()).all()
    return render_template('index.html', words=words)

@app.route('/add_word', methods=['POST'])
def add_word():
    english = request.form.get('english')
    uzbek = request.form.get('uzbek')
    example = request.form.get('example')
    
    if english and uzbek:
        new_word = Word(english=english, uzbek=uzbek, example=example)
        db.session.add(new_word)
        db.session.commit()
        flash('So\'z muvaffaqiyatli qo\'shildi!', 'success')
    else:
        flash('Inglizcha va o\'zbekcha tarjimalar kiritilishi shart!', 'error')
    
    return redirect(url_for('index'))

@app.route('/practice')
def practice():
    current_time = datetime.utcnow()
    words = Word.query.filter(
        Word.mastered == False,
        Word.next_review <= current_time
    ).order_by(Word.box_number).all()
    
    words_list = [word.to_dict() for word in words]
    return render_template('practice.html', words=words_list)

@app.route('/update_mastery/<int:word_id>', methods=['POST'])
def update_mastery(word_id):
    word = Word.query.get_or_404(word_id)
    is_correct = request.json.get('is_correct', False)
    
    word.update_box(is_correct)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'progress': word.get_progress(),
        'box_number': word.box_number,
        'mastered': word.mastered
    })

@app.route('/delete_word/<int:word_id>', methods=['POST'])
def delete_word(word_id):
    word = Word.query.get_or_404(word_id)
    db.session.delete(word)
    db.session.commit()
    flash('So\'z o\'chirildi!', 'success')
    return redirect(url_for('index'))

@app.route('/stats')
def stats():
    total_words = Word.query.count()
    mastered_words = Word.query.filter_by(mastered=True).count()
    words_by_box = db.session.query(Word.box_number, db.func.count(Word.id))\
        .group_by(Word.box_number).all()
    
    return render_template('stats.html', 
        total_words=total_words,
        mastered_words=mastered_words,
        words_by_box=dict(words_by_box)
    )

if __name__ == '__main__':
    app.run(debug=True)
