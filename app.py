#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from operator import add
from os import stat
import sys
from venv import create
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ARRAY, String
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm as BaseForm
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String())
    genres = db.Column(db.ARRAY(db.String(120)))
    shows = db.relationship('Show', backref='Venue', lazy='dynamic')

    def __init__(self, name, city, state, address, phone, image_link, facebook_link, website, seeking_talent, seeking_description, genres):
        self.name = name
        self.city = city
        self.state = state
        self.address = address
        self.phone = phone
        self.image_link = image_link
        self.facebook_link = facebook_link
        self.website = website
        self.seeking_talent = seeking_talent
        self.seeking_description = seeking_description
        self.genres = genres


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String)
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    # image_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist', lazy=True)

    def __repr__(self):
        return f'{__class__.__name__}(name={self.name}, )'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    start_time = db.Column(db.DateTime, nullable=False)

    def __init__(self, venue_id, artist_id, start_time):
        self.venue_id = venue_id
        self.artist_id = artist_id
        self.start_time = start_time

    def __repr__(self):
        return f'{__class__.__name__}(id={self.start_time}, )'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():

    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #  num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    venue_all = Venue.query.all()
    places = set()
    all_data = []
    for venue in list(venue_all):
        data = dict()
        time_now = datetime.now()
        all_upcoming_shows = venue.shows.filter(
            Show.start_time > time_now).all()

        if venue.state in places:
            all_data[-1]['venues'].append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len(all_upcoming_shows),
            })

        else:
            data['city'] = venue.city if venue.city != None else 'venue city'
            data['state'] = venue.state if venue.state != None else 'venue city'
            data['venues'] = [{
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len(all_upcoming_shows),
            }]
            places.add(venue.state)

        all_data.append(data)

    print(all_data)
    return render_template('pages/venues.html', areas=all_data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    search_term = '%' + search_term + '%'
    count = Venue.query.filter(Venue.name.ilike(search_term)).count()

    data = []
    for i in Venue.query.filter(Venue.name.ilike(search_term)):
        res = {
            'id': i.id,
            'name': i.name,
            'num_upcoming_shows': Show.query.filter_by(venue_id=i.id).filter(Show.start_time >= datetime.today()).count()
        }
        data.append(res)
        response = {
            'count': count,
            'data': data
        }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue_query = Venue.query.get(venue_id)
    data = dict()
    if venue_query:
        data['id'] = venue_query.id,
        data['name'] = venue_query.name
        data['genres'] = venue_query.genres
        data['address'] = venue_query.address
        data['city'] = venue_query.city
        data['phone'] = venue_query.phone
        data['website'] = venue_query.website
        data['facebook_link'] = venue_query.facebook_link
        data['seeking_talent'] = venue_query.seeking_talent
        data['seeking_description'] = venue_query.seeking_description
        data['image-link'] = venue_query.image_link
        past_shows = Show.query.options(db.joinedload(Show.Venue)).filter(
            Show.venue_id == venue_id).filter(Show.start_time <= datetime.now()).all()
        past_show_all = []
        for show in past_shows:
            past_show_all.append(
                {
                    'artist_id': show.artist_id,
                    'artist_name': show.Artist.name,
                    'artist_image_link': show.Artist.image_link,
                    'start_time':  show.start_time.strftime('%Y-%m-%d %H:M:%S')
                }
            )
        data['past_shows'] = past_show_all
        new_shows = Show.query.options(db.joinedload(Show.Venue)).filter(
            Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()
        new_show_all = []
        for show in new_shows:
            new_show_all.append(
                {
                    'artist_id': show.artist_id,
                    'artist_name': show.Artist.name,
                    'artist_image_link': show.Artist.image_link,
                    'start_time':  show.start_time.strftime('%Y-%m-%d %H:M:%S')
                }
            )
        data['upcoming_shows'] = new_show_all
        data['past_shows_count'] = len(past_show_all)
        data['upcoming_shows_count'] = len(new_show_all)

        return render_template('pages/show_venue.html', venue=data)
    return "{'error': 'venue not found'}"

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    # TODO: insert form data as a new Venue record in the db, instead

    if form.validate():
        try:
            created_venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                website=form.website.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data,
                genres=",".join(form.genres.data)
            )
            print(form.venue.data)
            db.session.add(created_venue)
            db.session.commit()

            # TODO: modify data to be the data object returned from db insertion
            # db.session.refresh(created_venue)
             # on successful db insert, flash success
            flash(f'Venue {created_venue.name} was successfully listed!')
            # Venue.insert(created_venue)

        except Exception as e:
            db.session.rollback()            
            print(sys.exc_info())
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            flash(f'Venue {created_venue.name} could not be created.')
        finally:
            db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists_all = Artist.query.all()
    # return render_template('pages/artists.html', artists=data)
    return render_template('pages/artists.html', artists=artists_all)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term: String = request.form['search_term']
    query = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
    response = {
        'count': len(list(query)),
        'data': []
    }
    for artist in query:
        response['data'].append(
            {
                'id': artist.id,
                'name': artist.name,
            }
        )
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist_query = Artist.query.get(artist_id)
    # TODO: replace with real artist data from the artist table, using artist_id
    data: dict = {}
    if artist_query:
        data['id'] = artist_query.id
        data['name'] = artist_query.name
        data['genres'] = artist_query.genres
        data['city'] = artist_query.city
        data['state'] = artist_query.state
        data['phone'] = artist_query.phone
        data['website'] = artist_query.website
        data['facebook_link'] = artist_query.facebook_link
        data['seeking_venue'] = artist_query.seeking_venue
        data['seeking_description'] = artist_query.seeking_description
        data['image_link'] = artist_query.image_link

        past_shows = Show.query.options(db.joinedload(Show.Artist)).filter(
            Show.artist_id == artist_id).filter(Show.start_time <= datetime.now()).all()
        past_show_all = []
        for show in past_shows:
            past_show_all.append(
                {
                    'venue_id': show.venue_id,
                    'venue_name': show.Venue.name,
                    'venue_image_link': show.Venue.image_link,
                    'start_time':  show.start_time.strftime('%Y-%m-%d %H:M:%S')
                }
            )
        data['past_shows'] = past_show_all
        new_shows = Show.query.options(db.joinedload(Show.Artist)).filter(
            Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
        new_show_all = []
        for show in new_shows:
            new_show_all.append(
                {
                    'venue_id': show.venue_id,
                    'venue_name': show.Venue.name,
                    'venue_image_link': show.Venue.image_link,
                    'start_time':  show.start_time.strftime('%Y-%m-%d %H:M:%S')
                }
            )
        data['upcoming_shows'] = new_show_all
        data['past_shows_count'] = len(past_show_all)
        data['upcoming_shows_count'] = len(new_show_all)

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    data: dict = {}
    if artist:
        form.name.data = artist.name,
        form.genres.data = artist.genres,
        form.city.data = artist.city,
        form.state.data = artist.state,
        form.phone.data = artist.phone,
        form.website_link.data = artist.website,
        form.facebook_link = artist.facebook_link,
        form.seeking_venue.data = artist.seeking_venue,
        form.seeking_description = artist.seeking_description,
        form.image_link.data = artist.image_link,

    # TODO: populate form with fields from artist with ID <artist_id>
        return render_template('forms/edit_artist.html', form=form, artist=artist)

    return "{'respond': 'could not find artist'}"


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)

    if form.validate():
        try:
            artist = Artist.query.get(artist_id)
            artist.name=form.name.data
            artist.city=form.city.data
            artist.state=form.state.data
            artist.phone=form.phone.data
            artist.website=form.website.data
            artist.genres=".".join(form.genres.data)
            artist.image_link=form.image_link.data
            artist.facebook_link=form.facebook_link.data
            artist.seeking_venue=form.seeking_venue.data
            artist.seeking_description=form.seeking_description.data

            db.session.add(artist)
            db.session.commit()
            flash(' Artist ' + artist.name + ' is successfully edited!')
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash(' Unsuccessful editing attempt.')
        finally:
            db.session.close()
        

        # TODO: take values from the form submitted, and update existing
        # artist record with ID <artist_id> using the new attributes

        return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    # venue = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    # }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm()
    
    if form.validate():
        try:
            venue=Venue.query.get(venue_id)
            venue.name=form.name.data
            venue.city=form.city.data
            venue.state=form.state.data
            venue.address=form.address.data
            venue.phone=form.phone.data
            venue.image_link=form.image_link.data
            venue.facebook_link=form.facebook_link.data
            venue.website=form.website.data
            venue.seeking_talent=form.seeking_talent.data
            venue.seeking_description=form.seeking_description.data
            venue.genres=",".join(form.genres.data)

            db.session.add(venue)
            db.session.commit()
            flash(" Venue " + venue.name + "successfully edited!")

        except Exception:
            db.session.rollback()
            print(sys.exc_info())
            flash("Unsuccessful editing attempt.")
        finally:
            db.session.close()
    else:
        flash("Unsuccessful editing attempt.")
         
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)

    if form.validate():
        try:
            created_artist = Artist(
                city=form.city.data,
                name=form.name.data,
                state=form.state.data,
                phone=form.phone.data,
                website=form.website.data,
                genres=",".join(form.genres.data)
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data,
            )
            db.session.add(created_artist)
            db.session.commit()
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
            
        except Exception:
            db.session.rollback()
            # TODO: on unsuccessful db insert, flash an error instead.
            flash(" Artist " + request.form['name']  + "could not be listed.")
        finally:
            db.session.close()
    else:
        flash(" Artist " + request.form['name']  + "could not be listed.")




    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = []
    for i in Show.query.all():
        data.append({
            "venue_id":i.venue_id,
            "venue_name":Venue.query.filter_by(id=i.venue_id).first().name,
            "artist_id":i.artist_id,
            "artist_name":Artist.query.filter_by(id=i.artist_id).first().name,
            "artist_image_link":Artist.query.filter_by(id=i.artist_id).first().image_link,
            "start_time":i.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    new_show = Show(
        venue_id=request.form['venue_id'],
        artist_id=request.form['artist_id'],
        start_time=request.form['start_time'],
    )
    try:
        Show.insert(new_show)
    except Exception as e:
        flash(f'An error occurred. Show couldn\'t be created')
    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
