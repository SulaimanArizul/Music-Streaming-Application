from flask import render_template, url_for, flash, redirect, request
from music import app,db,bcrypt
from music.models import User,Song,Creator,Album 
from flask_login import login_user,current_user,logout_user,login_required

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
  if current_user.is_authenticated:
    return redirect(url_for('home'))
  if request.method == 'POST':
    loginemail = request.form['email']
    password = request.form['password']
    user=User.query.filter_by(email=loginemail).first()
    if user and bcrypt.check_password_hash(user.password,password):
      login_user(user)
      flash('logined in successfully!','success')
      next_page = request.args.get('next')
      return redirect(next_page) if next_page else redirect(url_for('home'))
    else:
      flash('invalid email or password','danger')
      return redirect(url_for('user_login'))
  return render_template('user_login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('home'))
  if request.method == 'POST':
    login_type = request.form.get('login_type')
    if login_type == 'user':
      return redirect(url_for('user_login'))
    elif login_type == 'creator':
      return redirect(url_for('creator_login'))
  return render_template('login.html')


@app.route('/creator/login', methods=['GET', 'POST'])
def creator_login():
  if request.method == 'POST':
    creator_login = request.form.get('creator-login')
    if creator_login:
      flash('logined in successfully!','success')
      return redirect(url_for('creator'))
  return render_template('creator_login.html')

@app.route('/creator')
def creator():
  return render_template('creator.html')

@app.route('/user/profile')
@login_required
def user_profile():
  return render_template('user_profile.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method=='POST':
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    hashed_password=bcrypt.generate_password_hash(password).decode('UTF-8')
    if not username or not email or not password:
      return "All fields are required", 400
    else:
      user_exists = User.query.filter_by(username=username).first()
      email_exists = User.query.filter_by(email=email).first()

      if user_exists:
          flash('Username already taken.', 'error')
          return redirect(url_for('register'))

      if email_exists:
          flash('Email already registered.', 'error')
          return redirect(url_for('register'))
      user = User(username=username, email=email,password=hashed_password)
      db.session.add(user)
      db.session.commit()
      return redirect(url_for('user_login'))
    
  return render_template('register.html')

@app.route('/logout')
def logout():
  logout_user()
  flash('logged out successfully!')
  return redirect(url_for('home'))