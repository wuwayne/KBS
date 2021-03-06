from datetime import datetime
from hashlib import md5
from time import time

import jwt
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask import current_app

from app import db,login


followers = db.Table('followers',
	db.Column('follower_id',db.Integer,db.ForeignKey('user.id')),
	db.Column('followed_id',db.Integer,db.ForeignKey('user.id'))
)

thumb_ups = db.Table('thumb_ups',
	db.Column('thumbers_id',db.Integer,db.ForeignKey('user.id')),
	db.Column('thumbed_id',db.Integer,db.ForeignKey('post.id'))
)

stars = db.Table('stars',
	db.Column('starers_id',db.Integer,db.ForeignKey('user.id')),
	db.Column('stared_id',db.Integer,db.ForeignKey('post.id'))
)

class User(UserMixin,db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(64),index=True,unique=True)
	email = db.Column(db.String(64),index=True,unique=True)
	password_hash = db.Column(db.String(128))
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime,default=datetime.utcnow)

	posts = db.relationship('Post',backref='author',lazy='dynamic')
	comments = db.relationship('Comment',backref='author',lazy='dynamic')

	def __repr__(self):
		return '<User {}'.format(self.username)

	__str__ = __repr__

	def set_password(self,password):
		self.password_hash = generate_password_hash(password)

	def check_password(self,password):
		return check_password_hash(self.password_hash,password)

	def avatar(self,size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return r'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest,size)

	stared = db.relationship('Post',secondary=stars,
		backref=db.backref('starers',lazy='dynamic'),lazy='dynamic'
		)

	def star(self,post):
		if not self.is_staring(post):
			self.stared.append(post)

	def unstar(self,post):
		if self.is_staring(post):
			self.stared.remove(post)

	def is_staring(self,post):
		return self.stared.filter(stars.c.stared_id == post.id).count()>0


	thumbed = db.relationship('Post',secondary=thumb_ups,
		backref=db.backref('thumbers',lazy='dynamic'),lazy='dynamic'
		)

	def thumb(self,post):
		if not self.is_thumbing(post):
			self.thumbed.append(post)

	def unthumb(self,post):
		if self.is_thumbing(post):
			self.thumbed.remove(post)

	def is_thumbing(self,post):
		return self.thumbed.filter(thumb_ups.c.thumbed_id == post.id).count()>0

	followed = db.relationship('User',secondary=followers,
		primaryjoin=(followers.c.follower_id == id),
		secondaryjoin=(followers.c.followed_id == id),
		backref=db.backref('followers',lazy='dynamic'),lazy='dynamic'
		)

	def follow(self,user):
		if not self.is_following(user):
			self.followed.append(user)

	def unfollow(self,user):
		if self.is_following(user):
			self.followed.remove(user)

	def is_following(self,user):
		return self.followed.filter(followers.c.followed_id == user.id).count()>0

	def followed_posts(self):
		followed = Post.query.join(
			followers,(followers.c.followed_id == Post.user_id)).filter(
				followers.c.follower_id == self.id)
		own = Post.query.filter_by(user_id=self.id)
		return followed.union(own).order_by(Post.timestamp.desc())

	def get_reset_password_token(self,expires_in=600):
		return jwt.encode(
			{'reset_password':self.id,'exp':time()+expires_in},
			current_app.config['SECRET_KEY'],algorithm='HS256').decode('utf-8')

	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token,current_app.config['SECRET_KEY'],algorithm=['HS256'])['reset_password']
		except Exception as e:
			return
		return User.query.get(id)


@login.user_loader
def load_user(id):
	return User.query.get(int(id))

class Post(db.Model):
	__tablename__ = 'post'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	language = db.Column(db.String(5))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	comments = db.relationship('Comment',backref='mainpost',lazy='dynamic')

	def __repr__(self):
		return '<Post {}>'.format(self.body)

class Comment(db.Model):
	__tablename__ = 'comment'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	language = db.Column(db.String(5))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
