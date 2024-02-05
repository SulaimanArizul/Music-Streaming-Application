from sqlalchemy import func
from flask import render_template, url_for, flash, redirect, request,abort
from music import app,db,bcrypt
from music.models import User, Song, Creator,Album, Playlist, Rating
from flask_login import login_user,current_user,logout_user,login_required
import os
import secrets
from pydub import AudioSegment
from mutagen.mp3 import MP3
import ffmpeg
from datetime import datetime


@app.template_filter('to_datetime')
def to_datetime_filter(value, format='%Y-%m-%d %H:%M:%S.%f'):
    return datetime.strptime(value, format)


@app.route('/',methods=('GET','POST'))
def home():
  user_song = []

  if current_user.is_authenticated:
      total = Playlist.query.filter_by(user=current_user.id).all()
      song_ids = {playlist.songs for playlist in total}
      user_song = Song.query.filter(Song.id.in_(song_ids)).all()
  if request.method=='POST':
    song_id=request.form.get('song_id')
    song_now=request.form.get('play')
    play=Song.query.filter_by(id=song_now).first()
    liked=request.form.get('liked')
    rate=request.form.get('rate')
    if play:
      Songs = Song.query.all()
      distinct_genre = db.session.query(Song.genre).group_by(Song.genre).all()
      return render_template('home.html',songs=Songs,
                stream=play,user_song=user_song,genres=distinct_genre)
    if liked and current_user.is_authenticated:
      user_id=current_user.id
      songid=liked
      addplaylist=Playlist(user=user_id,songs=songid)
      db.session.add(addplaylist)
      db.session.commit()
    if liked and not current_user.is_authenticated:
      flash('Please login to like a song', 'danger')
    if rate and current_user.is_authenticated:
      user_id=current_user.id
      song_id=request.form.get('hidden_song_id')
      rating=rate
      existing_rating = Rating.query.filter_by(user=user_id, song=song_id).first()

      if existing_rating:
          # User has already rated this song
        flash('You have already rated this song.', 'warning')  
      else:  
        addRating=Rating(user=user_id, song=song_id, rating=rating)
        db.session.add(addRating)
        db.session.commit()
        average_rate = db.session.query(func.avg(Rating.rating)).filter(Rating.song == song_id).scalar()
        rounded_average = round(average_rate, 1)
        # Fetch the song from the database
        song_to_update = Song.query.get(song_id)
        if song_to_update:
            # Update the rating
            song_to_update.rating = rounded_average
            # Commit the changes to the database
            db.session.commit()
    if rate and not current_user.is_authenticated:
      flash('Please login to rate a song', 'warning')
    
  distinct_genre = db.session.query(Song.genre).group_by(Song.genre).all()
  Songs = Song.query.all()
  if current_user.is_authenticated:
    # user_song=Playlist.query(Playlist.songs).filter_by(user=current_user.id).all()
    total=Playlist.query.filter_by(user=current_user.id).all()
    song_ids = {playlist.songs for playlist in total}
    user_song = Song.query.filter(Song.id.in_(song_ids)).all()
    # user_songs=[x for x in total.song]
    return render_template('home.html',songs=Songs,user_song=user_song,genres=distinct_genre)
  return render_template('home.html',songs=Songs,genres=distinct_genre)

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
    # elif login_type == 'creator':
    #   return redirect(url_for('creator_login'))
  return render_template('login.html')


@app.route('/creator/login', methods=['GET', 'POST'])
@login_required
def creator_login():  
  if request.method == 'POST':
    creator_login = request.form.get('creator-login')
    if creator_login:
      current_user.iscreator=True
      id=current_user.id
      cusername=current_user.username
      cemail=current_user.email
      cpassword=current_user.password
      creator=Creator(id=id,name=cusername,email=cemail,password=cpassword)
      db.session.add(current_user)
      db.session.add(creator)
      db.session.commit()
      flash('logined in successfully!','success')
      return redirect(url_for('creator'))
  return render_template('creator_login.html')

@app.route('/creator')
@login_required
def creator():
  mysong=Song.query.filter_by(artist=current_user.id).all()
  artistname=current_user.username
  return render_template('creator.html',mysong=mysong,artistname=artistname)

@app.route('/user/profile')
@login_required
def user_profile():
  if current_user.iscreator:
    image=url_for('static',filename='profile_pic/creator_image.jpg')
  else:
    image=url_for('static',filename='profile_pic/user_image.jpg')
  return render_template('user_profile.html',image=image)

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

def save_song(song_file):
  random_hex=secrets.token_hex(8)
  _,f_ext=os.path.splitext(song_file.filename)
  song_n=random_hex+f_ext
  song_path=os.path.join(app.root_path,'static/saved_songs'
                         ,song_n)
  song_file.save(song_path)
  return song_n
  
  
@app.route('/creator/upload', methods=['GET', 'POST'])
@login_required
def creator_upload():
  if request.method == 'POST':
    name=request.form.get('title')
    genre=request.form.get('genre')
    lyrics=request.form.get('lyrics')
    artist=current_user.id
    album=request.form.get('album_name')
    song_file=request.files.get('file')
    saved_song=save_song(song_file)
    song_path=os.path.join(app.root_path,'static/saved_songs'
       ,saved_song)
    audio = MP3(song_path)
    duration_in_seconds = audio.info.length
    minutes = int(duration_in_seconds // 60)
    seconds = int(duration_in_seconds % 60)
    duration = f"{minutes:02d}:{seconds:02d}"
    album1=Album.query.filter_by(name=album).first()
    if album1:
      song=Song(title=name,artist=artist,genre=genre,
        album_id=album1.id,file=saved_song,lyrics=lyrics,duration=duration)
      db.session.add(song)
      db.session.commit()
    else:  
      album=Album(name=album,artist=artist)
      db.session.add(album)
      db.session.commit()
      song=Song(title=name,artist=artist,genre=genre,
        album_id=album.id,file=saved_song,lyrics=lyrics, 
                duration=duration)
      db.session.add(song)
      db.session.commit()
    return redirect(url_for('creator'))  
  return render_template('creator_upload.html')

@app.route('/creator/update/<int:song_id>', methods=['GET','POST'])
@login_required
def creator_update(song_id):
  song = Song.query.get_or_404(song_id)
  
  if current_user.id != song.artist:
      abort(403)
  
  if request.method == 'POST':
      title = request.form.get('title')
      genre = request.form.get('genre')
      songfile = request.files.get('file')
      album=request.form.get('album_name')
      lyrics=request.form.get('lyrics')
  
      # Update the title and genre if they are provided
      if title:
          song.title = title
      if genre:
          song.genre = genre

      if album:
        song.album_id = album

      if lyrics:
        song.lyrics=lyrics
  
      # Update the file only if a new file is uploaded
      if songfile:
          saved_song = save_song(songfile)
          song.file = saved_song
  
      db.session.commit()
      return redirect(url_for('creator', song_id=song.id))
  
  return render_template('creator_update.html', song=song)

@app.route('/creator/delete/<int:song_id>', methods=['GET', 'POST'])
@login_required
def creator_delete(song_id):
  song=Song.query.get_or_404(song_id)
  if current_user.id != song.artist:
    abort(403)
  db.session.delete(song)
  db.session.commit()
  flash('Your song has been deleted!', 'success')
  return redirect(url_for('creator'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
  admimemail='23dp1000004@ds.study.iitm.ac.in'
  adminpassword='admin'
  if request.method == 'POST':
    email=request.form.get('email')
    password=request.form.get('password')
    user=User.query.filter_by(email=email).first()
    if email==admimemail and password==adminpassword and user:
      flash('you have logged-in in successfully!','success')
      return redirect(url_for('admin'))
    else:
      if email!=admimemail:
        flash('invalid email','danger')
      if password!=adminpassword:
        flash(f'invalid password','danger')
      return redirect(url_for('admin_login'))  
  return(render_template('admin_login.html'))  

@app.route('/admin', methods=['GET', 'POST'])
def admin():
  songs=Song.query.all()
  totalsong=Song.query.count()
  totalalbum=Album.query.count()
  totaluser=User.query.count()
  totalartist=Creator.query.count()
  return render_template('admin.html',songs=songs,totalsong=totalsong,totalalbum=totalalbum,totaluser=totaluser,totalartist=totalartist)
      
@app.route('/admin/delete/<int:song_id>', methods=['GET', 'POST'])
def admin_delete(song_id):
  song=Song.query.get_or_404(song_id)
  db.session.delete(song)
  db.session.commit()
  flash('Your song has been deleted!', 'success')
  return redirect(url_for('admin'))
@app.route("/user/search", methods=['GET', 'POST'])
def user_search():
  if request.method == 'POST':
    search_query = request.form.get('searched')
    song_now=request.form.get('play')
    play=Song.query.filter_by(id=song_now).first()
    liked=request.form.get('liked')
    if play:
      songs = Song.query.filter(Song.title.ilike(f'%{search_query}%')).all()
      Songs = Song.query.all()
      distinct_genre = db.session.query(Song.genre).group_by(Song.genre).all()
      return render_template('user_search.html',
                stream=play,search_query=search_query,songs=songs)
    if liked and current_user.is_authenticated:
      user_id=current_user.id
      songid=liked
      addplaylist=Playlist(user=user_id,songs=songid)
      db.session.add(addplaylist)
      db.session.commit()
    if search_query:
      songs = Song.query.filter(Song.title.ilike(f'%{search_query}%')).all()
      return render_template('user_search.html', songs=songs, search_query=search_query)
    else:
      flash('Please enter a search query.', 'danger')
      return redirect(url_for('user_search'))
  return render_template('user_search.html')
  