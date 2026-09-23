from flask import Flask, render_template, request, session, redirect, url_for, jsonify # Imports all the Flask tools
from questions import questions # Imports questions from the questions.py file
from dotenv import load_dotenv # Imports the load_dotenv function from the dotenv module
import requests # Sends HTTP requests
import os
import sqlite3
from util import get_random_question # Imports the function to get random questions

# API setup
load_dotenv()

# Get API key
API_KEY = os.getenv("API_KEY") # Gets the API key from the env file
SECRET_KEY = os.getenv("SECRET_KEY") # Gets the secret key from the env file
BASE_URL = "https://api.weatherapi.com/v1/current.json"
question_amount = 20 # Sets the amount of questions to 20

# Create Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY # Sets the secret key for the session

# Home route
@app.route("/")
# Home page
def home():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
# Starts the quiz
def start():
    session["name"] = request.form["name"] # Gets the name from the form
    random_question_list = get_random_question(questions, question_amount) # Gets random questions
    session["questions_id"] = random_question_list # Saves the question IDs in the session
    session["score"] = 0 # Sets the starting score to 0
    session["current_question"] = 0 # Starts at the first question
    return redirect(url_for("choose")) # Sends the user to the quiz page

@app.route("/choose")
def choose():
    return render_template("choose.html")

# Quiz route
@app.route("/quiz")
# Shows the quiz page
def quiz():
    name = session["name"]
    questions_id = session["questions_id"]
    current_question = session["current_question"]
    # Checks if all the questions have been completed
    if current_question >= len(questions_id):
        return redirect(url_for("finish"))
    return render_template(
        "quiz.html",
        questions=questions[questions_id[current_question]],
        name=name,
        current_question=current_question + 1
    )

@app.route("/answer", methods=["POST"])
def answer():
    user_answer = int(request.form["answer"]) # Gets the user's answer from the form
    current_question = session["current_question"]
    # Checks that the question exists before accessing it
    if current_question >= len(session["questions_id"]):
        return redirect(url_for("finish"))
    questions_id = session["questions_id"][current_question]
    question = questions[questions_id]
    # Checks if the user's answer is correct
    if user_answer == question["answer"]:
        session["score"] += 1
    session["current_question"] += 1
    # Checks if the quiz is finished
    if session["current_question"] >= len(session["questions_id"]):
        return redirect(url_for("finish"))
    return redirect(url_for("quiz"))

@app.route("/finish")
def finish():
    name = session["name"]
    score = session["score"]
    total = len(session["questions_id"])
    # Finds the user in the database
    user = find_user(name)
    attempts = 0
    # Gets the user's previous attempts
    if user:
        attempts = get_attempts(user[0])
    attempts += 1
    attempts = add_suffix(attempts)
    # Creates a new user if they don't already exist
    if not user:
        user = save_user(name)
    # Calculates the user's score percentage
    score_percentage = calculate_score_percentage(score, question_amount)
    user_id = user[0]
    save_score(user_id, score, score_percentage)
    return render_template(
        "finish.html",
        score_percentage=score_percentage,
        score=score,
        name=name,
        attempts=attempts,
        question_amount=question_amount
    )

@app.route("/results-quiz")
def results():
    list_of_results = get_results() # Gets the results from the database
    print(list_of_results)
    return render_template(
        "results-quiz.html",
        list_of_results=list_of_results,
        question_amount=question_amount
    )

@app.route("/game")
def game():
    name = session["name"]
    return render_template(
    "game.html",
    name=name)

# Weather route
@app.route("/weather", methods=["GET", "POST"])
def weather():
    # Sets the starting values
    weather = None
    error = None
    if request.method == "POST":
        city = request.form.get("city") # Gets the city from the form
        # Checks if the user entered a city
        if not city:
            error = "Please enter a city."
        else:
            params = {
                "key": API_KEY,
                "q": city,
                "aqi": "no"
            }
            # Sends a request to the weather API
            try:
                response = requests.get(BASE_URL, params=params)
                # Checks if the API request was successful
                if response.status_code == 200:
                    weather = response.json()
                else:
                    error = "Could not find that location."
            # Shows an error if the API cannot be reached
            except requests.RequestException:
                error = "There was a problem connecting to the weather service."
    return render_template(
        "weather.html",
        weather=weather,
        error=error
    )

@app.route("/results-game")
def results_game():
    list_of_score=get_score()
    print(list_of_score)
    return render_template(
        "results-game.html",
        list_of_score=list_of_score
    )

@app.route("/save_score", methods=["POST"])
def save_game():
    data = request.get_json()
    name = data["name"]
    user = find_user(name)
    if not user:
        user = save_user(name)
    print(user, 111)
    user_id = user[0]
    save_score_game(data["score"], user_id)
    return jsonify({
        "success": True,
        "message": "Form submitted successfully!"
    })

# Saves a new user to the database
def save_user(name):
    connection = sqlite3.connect("quiz.db")
    cursor = connection.cursor()
    user = cursor.execute(
        "INSERT INTO users (name) VALUES (?)",
        (name,)
    )
    connection.commit()
    connection.close()
    return user


def save_score_game(score, user_id):
    connection = sqlite3.connect("quiz.db")
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO score (score, user_id) VALUES (?, ?)",
        (score, user_id)
    )
    connection.commit()
    connection.close()

# Saves the user's score to the database
def save_score(user_id, score, score_percentage):
    connection = sqlite3.connect("quiz.db")
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO results (score, score_percentage, user_id) VALUES (?, ?, ?)",
        (score, score_percentage, user_id)
    )
    connection.commit()
    connection.close()

# Calculates the score percentage
def calculate_score_percentage(score, question_amount):
    score_percentage = score / question_amount * 100
    return score_percentage

# Gets the number of attempts for a user
def get_attempts(id):
    connection = sqlite3.connect("quiz.db")
    cursor = connection.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM results WHERE user_id = ?",
        (id,)
    )
    attempts = cursor.fetchone()[0]
    connection.close()
    return attempts

# Finds a user by their name
def find_user(name):
    connection = sqlite3.connect("quiz.db")
    cursor = connection.cursor()
    user = cursor.execute(
        "SELECT * FROM users WHERE name = ?",
        (name,)
    ).fetchone()
    connection.close()
    return user

# Adds the correct suffix to the attempt number
def add_suffix(attempts):
    str_attempts = str(attempts)
    if attempts == 1:
        return str_attempts + "st"
    elif attempts == 2:
        return str_attempts + "nd"
    elif attempts == 3:
        return str_attempts + "rd"
    else:
        return str_attempts + "th"

# Gets the quiz results from the database
def get_results():
    connection = sqlite3.connect("quiz.db")
    cursor = connection.cursor()
    cursor.execute(
        "SELECT u.name, r.score, r.score_percentage FROM users u LEFT JOIN results r ON u.id = r.user_id LIMIT 100;"
    )
    results = cursor.fetchall()
    connection.close()
    return results

def get_score():
    connection = sqlite3.connect("quiz.db")
    cursor = connection.cursor()
    cursor.execute(
        "SELECT u.name, r.score FROM users u LEFT JOIN score r ON u.id = r.user_id ORDER BY r.score DESC LIMIT 100;"
    )
    results = cursor.fetchall()
    print(results)
    connection.close()
    return results

# Starts the Flask application
if __name__ == "__main__":
    import os
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )