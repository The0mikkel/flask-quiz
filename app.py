import os
from flask import Flask, request, render_template, session, redirect, url_for, jsonify
import json
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

def get_quizzes():
    with open("questions.json", "r") as f:
        questions = json.load(f)
    return questions

def reset_session():
    session['quiz'] = {
            'question': None,
            'correct_answers': None,
            'remaining_answers': None,
        }
    session['questions'] = None

def select_question():
    if 'questions' not in session or session['questions'] == None or len(session['questions']) == 0:
        session['questions'] = get_quizzes()
                
    question = random.choice(session['questions'])
    session['questions'].remove(question)
    
    return question["question"], question["answers"]

def check_answer(correct_answers, answer, get_index = False):
    answer = answer.lower()
    
    for correct_answer in correct_answers:
        if correct_answer.lower() == answer:
            if get_index:
                return correct_answers.index(correct_answer)
            else:
                return True

    return -1

def set_question():
    if 'quiz' not in session:
        reset_session()
    if session['quiz']['question'] is None:
        question, correct_answers = select_question()
        session['quiz']['question'] = question
        session['quiz']['correct_answers'] = correct_answers
        session['quiz']['remaining_answers'] = correct_answers.copy()

@app.route('/complete')
def complete():
    if 'quiz' not in session:
        return redirect(url_for('home'))
        
    correctly_answered_list = []
    for answer in session['quiz']['correct_answers']:
        if answer not in session['quiz']['remaining_answers']:
            correctly_answered_list.append(answer)
            
    previous_question = session['quiz']['question']
    
    session['quiz']['question'] = None
    session.modified = True
    set_question()
    
    return render_template('complete.html', question=previous_question, correctly_answered_list=correctly_answered_list)

@app.route('/reset')
def reset():
    reset_session()
    return redirect(url_for('home'))

@app.route('/done')
def done():
    reset_session()
    return render_template('done.html', rerun_url=url_for('index'))

@app.route('/done-select')
def done_select():
    reset_session()
    return render_template('done.html', rerun_url=url_for('quiz_select'))

@app.route('/quiz', methods=['GET', 'POST'])
def index():
    set_question()
    
    success = None
    
    message = ''
    if request.method == 'POST':
        answer = request.form.get('answer')
        if answer == "quit":
            app.session_interface.clear_session(app, session)
            return "Du har valgt at stoppe spillet"
        correct = check_answer(session['quiz']['correct_answers'], answer, True)
        if not correct == -1:
            if not check_answer(session['quiz']['remaining_answers'], answer):
                message = "Det har du allerede svaret på!"
                success = False
            else:
                message = f"Korrekt! Du har {len(session['quiz']['remaining_answers']) - 1} svar tilbage (ID: {correct})"
                session['quiz']['remaining_answers'].remove(answer.lower())
                success = True
        else:
            message = f"Forkert! Du har {len(session['quiz']['remaining_answers'])} svar tilbage"
            success = False
    
    correctly_answered_list = []
    for answer in session['quiz']['correct_answers']:
        if answer not in session['quiz']['remaining_answers']:
            correctly_answered_list.append(answer)
            
    session.modified = True
    
    if len(session['quiz']['remaining_answers']) == 0:
        if len(session['questions']) == 0:
            return redirect(url_for('done'))
    
        return redirect(url_for('complete'))
    
    if success == True:
        success = 'is-valid'
    elif success == False:
        success = 'is-invalid'
    else:
        success = ''
    
    return render_template('quiz.html', question=session['quiz']['question'], message=message, correctly_answered_list=correctly_answered_list, answers_list=session['quiz']['correct_answers'], success=success)

@app.route('/quiz-select', methods=['GET', 'POST'])
def quiz_select():
    if request.method == 'POST':
        data = request.get_json()
        selected_answers = data.get('answers', [])
        correct_answers = session.get('correct_answers', [])
        
        if len(selected_answers) != len(correct_answers):
            return jsonify({'message': f"Forkert, du har enten valgt for mange eller for få svarmuligheder."}), 400
        
        for i in range(len(selected_answers)):
            selected_answers[i] = selected_answers[i].lower()
            
            if selected_answers[i] not in correct_answers:
                return jsonify({'message': 'Forkert, du har valgt et svar der ikke er korrekt.'}), 400
        
        return jsonify({'message': 'Korrekt! Siden vil nu genindlæses.'}), 200
    else:
        question, correct_answers, possible_answers = select_multiple_choice_question()
        if question is None:
            return redirect(url_for('done_select'))
        
        session['correct_answers'] = correct_answers
        return render_template('quiz_select.html', question=question, possible_answers=possible_answers)

def select_multiple_choice_question():
    if 'questions' not in session or session['questions'] == None:
        session['questions'] = get_quizzes()
        
    if len(session['questions']) == 0:
        return None, None, None
                
    question = random.choice(session['questions'])
    session['questions'].remove(question)
    
    correct_answers = question["answers"]
    all_answers = [ans for q in get_quizzes() for ans in q['answers']]
    
    all_answers = [answer.lower() for answer in all_answers]
    correct_answers = [answer.lower() for answer in correct_answers]

    all_answers = [answer for answer in all_answers if answer not in correct_answers]
    
    random.shuffle(all_answers)
    
    possible_answers = correct_answers + all_answers[:int((0.5 * len(correct_answers)) + 4)]
    random.shuffle(possible_answers)
    
    return question["question"], correct_answers, possible_answers

@app.route('/')
def home():
    return render_template('home.html', quizzes=get_quizzes())

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
