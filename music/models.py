from music import db,login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model,UserMixin):
  id=db.Column(db.Integer,primary_key=True)
  username=db.Column(db.String(20),unique=True,nullable=False)
  email=db.Column(db.String(120),unique=True,nullable=True)
  password=db.Column(db.String(50),nullable=False)
  iscreator=db.Column(db.Boolean,default=False)

  def __repr__(self):
   return f"User('{self.username}','{self.email}','{self.iscreator}')"

class Song(db.Model):
  id=db.Column(db.Integer,primary_key=True)
  title=db.Column(db.String(50),nullable=False)
  artist=db.Column(db.Integer,db.ForeignKey('creator.id'),
                   nullable=False,)
  album_id=db.Column(db.Integer,db.ForeignKey('album.id'),
                  nullable=False)
  file=db.Column(db.String(50),nullable=False)
  genre=db.Column(db.String(50),nullable=False)
  date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  lyrics=db.Column(db.Text,nullable=False,default='not yet uploaded')
  rating=db.Column(db.Integer,default=0)
  duration=db.Column(db.Integer,nullable=False,default=0)

  creator = db.relationship('Creator', backref='songs')

  def __repr__(self):
     return f"Song('{self.title}','{self.artist}','{self.album}')"

class Creator(db.Model,UserMixin):
  id=db.Column(db.Integer,primary_key=True)
  name=db.Column(db.String(50),nullable=False)
  email=db.Column(db.String(120),unique=True,nullable=False)
  password=db.Column(db.String(50),nullable=False)
  album=db.relationship('Album',backref='creator',lazy=True)
  rating=db.Column(db.Integer,default=0)

  def __repr__(self):
    return f"Creator('{self.name}','{self.email}','{self.rating}')"

class Album(db.Model):
  id=db.Column(db.Integer,primary_key=True)
  name=db.Column(db.String(50),nullable=False,unique=True)
  rating=db.Column(db.Integer,default=0)
  artist=db.Column(db.String(50),db.ForeignKey('creator.id'), nullable=False)
  songs=db.relationship('Song',backref='album',lazy=True)

  def __repr__(self):
    return f"Album('{self.name}','{self.rating}','{self.artist}')"

class Playlist(db.Model):
  id=db.Column(db.Integer,primary_key=True)
  user=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
  songs=db.Column(db.Integer,db.ForeignKey('song.id'),nullable=False)

class Rating(db.Model):
  id=db.Column(db.Integer,primary_key=True)
  song=db.Column(db.Integer,db.ForeignKey('song.id'),nullable=False)
  user=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
  rating=db.Column(db.Integer,nullable=False)
  # Unique constraint to ensure a user can rate a specific song only once
  __table_args__ = (db.UniqueConstraint('user', 'song', name='user_song_uc'),)