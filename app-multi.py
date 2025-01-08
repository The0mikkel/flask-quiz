import os
from flask import Flask, request, render_template, session, redirect, url_for, jsonify
import json
import random
from datetime import datetime
from flask_misaka import Misaka

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
Misaka(app)

def get_quizzes():
    try:
        with open("quizzes/quizzes.json", "r") as f:
            return json.load(f)
    except:
        return []
    
def quiz_info(name):
    quizzes = get_quizzes()
    
    for quiz in quizzes:
        if quiz["file_name"] == name:
            return quiz
        
    return None

def get_quizz(name):
    try:
        quizzes = get_quizzes()
        
        found = False
        file_name = ""
        for quiz in quizzes:
            if quiz["file_name"] == name:
                found = True
                file_name = quiz["file_name"]
                break
    
        with open('quizzes/' + name + ".json", "r") as f:
            return json.load(f)
    except:
        return []

def reset_session():
    session['quiz_select'] = None
    session['correct_answers'] = None
    session['questions'] = None
    session['completed_questions'] = []

@app.route('/reset')
def reset():
    reset_session()
    return redirect("/")

@app.route('/done')
def done():
    quiz = quiz_info(session['quiz_select'])
    reset_session()
    return render_template('done.html', rerun_url="/", quiz=quiz)

@app.route('/done-select')
def done_select():
    quiz = quiz_info(session['quiz_select'])
    reset_session()
    return render_template('done.html', rerun_url=url_for('quiz_select'), quiz=quiz)

@app.route('/quiz-select/answers', methods=['GET'])
def quiz_select_answers():
    if (session['quiz_select'] if 'quiz_select' in session else None) is None:  
        return redirect(url_for('reset'))
    
    return jsonify({'message': 'Giving up, I see?', 'answers': session['correct_answers']}), 200

@app.route('/quiz-select', methods=['GET', 'POST'])
def quiz_select():    
    if (session['quiz_select'] if 'quiz_select' in session else None) is None:
        return redirect(url_for('reset'))
        
    if request.method == 'POST':
        data = request.get_json()
        selected_answers = data.get('answers', [])
        correct_answers = session.get('correct_answers', [])
        
        if len(selected_answers) != len(correct_answers):
            return jsonify({'message': "Incorrect, you have either selected too many or too few options."}), 400
        
        for i in range(len(selected_answers)):
            selected_answers[i] = selected_answers[i].lower()
            
            if selected_answers[i] not in correct_answers:
                return jsonify({'message': 'Incorrect, you have selected an answer that is not correct.'}), 400
        
        return jsonify({'message': 'Correct!', 'answers': selected_answers}), 200
    else:
        question, correct_answers, possible_answers, description = select_multiple_choice_question()
        if question is None:
            return redirect(url_for('done_select'))
        
        quiz = quiz_info(session['quiz_select'])
        
        quiz['questions_answered'] = len(session['completed_questions'])
        quiz['questions_total'] = len(session['completed_questions']) + len(session['questions'])
    
        session['correct_answers'] = correct_answers
        return render_template('quiz_select.html', question=question, possible_answers=possible_answers, description=description, quiz=quiz, correct_answers_len=len(correct_answers))

def select_multiple_choice_question():
    questions = get_quizz(session['quiz_select'])
    if 'questions' not in session or session['questions'] == None:
        # Only store question index not the answers
        session['questions'] = list(range(len(questions)))

    if len(session['questions']) == 0:
        return None, None, None, None
                
    question = random.choice(session['questions'])
    session['questions'].remove(question)
    session['completed_questions'] = (session['completed_questions'] if 'completed_questions' in session else []) + [question]
    
    # Get question from file
    if (question < 0 or question >= len(questions)):
        return None, None, None, None
    
    question = questions[question]
    
    question_type = (question["type"] if "type" in question else "Standard")
    
    correct_answers = (question["answers"] if "answers" in question else [])
    wrong_answers = (question["wrong_answers"] if "wrong_answers" in question else [])
    
    # Specified question have defined correct and wrong answers
    if question_type == "Specified":
        all_answers = wrong_answers + correct_answers
    else:
        all_answers = [ans for q in get_quizz(session['quiz_select']) for ans in q['answers']]
        
    all_answers = [answer.lower() for answer in all_answers]
    correct_answers = [answer.lower() for answer in correct_answers]

    wrong_answers = [answer for answer in all_answers if answer not in correct_answers]
    
    random.shuffle(wrong_answers)
    
    if question_type == "Specified":
        possible_answers = correct_answers + wrong_answers
    else:
        possible_answers = correct_answers + wrong_answers[:int((0.5 * len(correct_answers)) + 4)]
        
    random.shuffle(possible_answers)
    
    description = (question["description"] if "description" in question else "")
    
    question = (question["question"] if "question" in question else "")
    
    return question, correct_answers, possible_answers, description

@app.route('/')
def quiz():
    return render_template('select_quiz.html', quizzes=get_quizzes())

@app.route('/quiz/<quiz_name>')
def quiz_name(quiz_name):
    session['quiz_select'] = quiz_name
    session['questions'] = None
    session['completed_questions'] = []
    info = quiz_info(quiz_name)
    
    if info is None:
        return redirect("/")
    
    return render_template('home.html', quiz=info, quizzes=get_quizz(session['quiz_select']))

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)