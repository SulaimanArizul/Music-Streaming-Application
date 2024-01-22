from music import db,login_manager
from flask_login import UserMixin

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
  artist=db.Column(db.String(50),db.ForeignKey('creator.id'),
                   nullable=False,)
  album=db.Column(db.String(50),db.ForeignKey('album.id'),nullable=False)
  duration=db.Column(db.String(50),nullable=False)
  genre=db.Column(db.String(50),nullable=False)
  rating=db.Column(db.Integer,default=0)

  def __repr__(self):
     return f"Song('{self.title}','{self.artist}','{self.album}')"

class Creator(db.Model):
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
  name=db.Column(db.String(50),nullable=False)
  rating=db.Column(db.Integer,default=0)
  artist=db.Column(db.String(50),db.ForeignKey('creator.id'), nullable=False)
  songs=db.relationship('Song',backref='albumodasong',lazy=True)

  def __repr__(self):
    return f"Album('{self.name}','{self.rating}','{self.artist}')"
