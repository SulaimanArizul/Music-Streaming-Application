from flask import Flask, render_template, request, redirect, url_for,flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

User=[
  {
    'username':'sulaiman',
    'email':'sulaiman@gmail.com'
  }
]

Songs=[
  {
    'song_name':'song1',
    'artist':'artist1'
  },
  {
    'song_name':'song2',
    'artist':'artist2'
  },
  {
    'song_name':'song3',
    'artist':'artist3'
  },
  {
    'song_name':'song4',
    'artist':'artist4'
  },
  {
    'song_name':'song5',
    'artist':'artist5'
  }
]

@app.route('/')
def home():
  return render_template('home.html',songs=Songs)

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == "abc@gmail.com" and password == "password":
            flash("you have logged-in","success")
            return redirect(url_for('home'))
        else:
            flash('invalid email or password','danger')
            return "Invalid credentials", 401
    return render_template('user_login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_type = request.form.get('login_type')
        if login_type == 'user':
            return redirect(url_for('user_login'))
        elif login_type == 'creator':
            return redirect(url_for('creator_login'))
    return render_template('login.html')


@app.route('/creator/login', methods=['GET', 'POST'])
def creator_login():
    return render_template('creator_login.html')

@app.route('/creator')
def creator():
  return render_template('creator.html')

@app.route('/user/profile')
def user_profile():
  return render_template('user_profile.html')



if __name__=='__main__':
  app.run(host='0.0.0.0',debug=True)
  