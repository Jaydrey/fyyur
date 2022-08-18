from datetime import datetime
# from app import db
from flask_sqlalchemy import SQLAlchemy
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
db = SQLAlchemy()

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text)
    genres = db.Column(db.ARRAY(db.String(120)))
    created_date = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    shows = db.relationship('Show', backref='venues', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'{__class__.__name__}(name=\'{self.name}\')'


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(300))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(120))
    created_date = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    shows = db.relationship('Show', backref='artists', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'{__class__.__name__}(name={self.name}, )'

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'{__class__.__name__}(id={self.start_time}, )'