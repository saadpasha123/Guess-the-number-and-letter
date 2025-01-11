from flask import Flask,request,session,render_template,flash,redirect,url_for
import json
import random
import pyttsx3
import string
app = Flask(__name__)
app.secret_key = '123'

def load_user():
    try:
        with open("user.json","r")as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_user(user):
    with open("user.json","w")as file:
        json.dump(user,file,indent=4)

def speak(remarks):
    engine=pyttsx3.init()
    engine.say(remarks)
    engine.runAndWait()

@app.route('/')
def home():
    username=session.get('username')
    return render_template('index.html', username=username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        user=load_user()

        if any(users['username']==username for users in user):
            flash('username already exist')
        else:
            user.append({'username':username, 'password':password}) 
            save_user(user)
            flash('You have successfully register')
            return redirect(url_for('login'))
    return render_template('register.html')        

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        user=load_user()
        for u in user:
            if u['username']==username and u['password']==password:
                session['username']=username
                flash('LOGIN SUCCESSFULLY')
                return redirect(url_for('home'))
            else:
                flash('INVALID USERNAME OR PASSWORD')
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('username',None)
    flash('YOU HAVE SUCCESSFULLY LOGOUT!')
    return redirect(url_for('home'))

@app.route('/game_style', methods=['POST'])
def game_style():
    game_style=request.form['game_style']
    difficult=request.form['difficult']
    session['game_style']=game_style
    session['difficult']=difficult
    session['limit_attempt']=3

    if game_style=='numbers':
        if difficult=='easy':
            session['target']=random.randint(1,25)
        elif difficult=='medium':
            session['target']=random.randint(26,99)
        elif difficult=='hard':
            session['target']=random.randint(100,1000)
    elif game_style=='letter':
        session['target']=random.choice(string.ascii_lowercase)
    session['attempt']=0
    session['remarks']=None
    return redirect(url_for('play_game'))

@app.route('/play_game')
def play_game():
    game_style=session.get("game_style", "")
    remarks=session.get("remarks", "")
    return render_template('play_game.html', game_style=game_style, remarks=remarks)        

@app.route('/guess', methods=["POST"])
def guess():
    print('session data',session)
    print('guess recieved',request.form['guess'])
    if 'game_style' not in session or 'target' not in session:
        flash('Start the game again!')
        return redirect(url_for('home'))
    if 'attempt' not in session:
        session['attempt']=0    
    guess=request.form['guess'].lower()
    target=session.get('target')
    game_style=session.get('game_style')
    limit_attempt=session.get('limit_attempt')
    remarks=""

    if session['attempt']>=limit_attempt:
        remarks="Soooooooooooory you have try more than your limitation, so please start a new game!"
        session['remarks']=remarks
        speak(remarks)
        return redirect(url_for('play_game'))
    if game_style=='numbers':
         try:
            guess=int(guess)
            if guess<target:
                remarks="Not quite there, aim higher!"
            elif guess>target:
                remarks="Not quite there, aim lower!"
            else:
                remarks=f"Fantastic! You found the correct number in {session['attempt']+1} attempts!"
                if session['difficult']=='easy':
                    session['target']=random.randint(1,25)
                elif session['difficult']=='medium':
                    session['target']=random.randint(26,50)
                elif session['difficult']=='hard':
                    session['target']=random.randint(456,1000)
         except ValueError:
            remarks="Invalid input! Please enter a valid number."
    elif game_style=='letter':
        if len(guess)!=1 or not guess.isalpha():
            remarks='INVALID INPUT, PLEASE TYPE A SINGLE ALPHABETIC CHARACTER!'
        elif guess<target:
            remarks='YOUR GUESS IS ALPHABETICALLY Not quite there, aim higher!'
        elif guess>target:
            remarks="YOUR GUESS IS ALPHABETICALLY Not quite there, aim lower!"
        else:
            remarks=f'Fantastic! You found the correct letter in {session['attempt']+1} attempts!'
            session['target']=random.choice(string.ascii_lowercase)
    speak(remarks)
    session['remarks']=remarks
    session['attempt']+=1
    print('update remarks',remarks)
    return redirect(url_for('play_game'))

if __name__ =='__main__':
    app.run(debug=True)
