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


#


from flask import (Flask,
                   render_template,
                   request,
                   Response,
                   flash,
                   redirect,
                   url_for)
from flask_moment import Moment
from flask_migrate import Migrate

from sqlalchemy import (ARRAY,
                        String,
                        desc)



import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm as BaseForm
from forms import *
from models import db,  Artist, Venue, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

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
    venues = Venue.query.order_by(desc(Venue.created_date)).limit(10).all()
    artists = Artist.query.order_by(desc(Artist.created_date)).limit(10).all()
    return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

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

    if form.validate_on_submit():

        created_venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            website=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data,
        )

        try:
            db.session.add(created_venue)
            db.session.commit()
            flash(f'Venue {created_venue.name} was successfully listed!')

        except Exception as e:
            db.session.rollback()
            print(sys.exc_info())
            print(e)
            flash(f'Venue {created_venue.name} could not be created.')
        finally:
            db.session.close()

        print(form.errors)
        # flash(f'Venue could not be created.')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
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
    artist_query = Artist.query.get(artist_id)
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

        past_shows = Show.query.options(db.joinedload(Show.artist)).filter(
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
        new_shows = Show.query.options(db.joinedload(Show.artist)).filter(
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

        return render_template('forms/edit_artist.html', form=form, artist=artist)

    return "{'respond': 'could not find artist'}"


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)

    if form.validate():
        try:
            artist = Artist.query.get(artist_id)
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.website = form.website.data
            artist.genres = ".".join(form.genres.data)
            artist.image_link = form.image_link.data
            artist.facebook_link = form.facebook_link.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data

            db.session.add(artist)
            db.session.commit()
            flash(' Artist ' + artist.name + ' is successfully edited!')
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash(' Unsuccessful editing attempt.')
        finally:
            db.session.close()

        return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm()

    if form.validate():
        try:
            venue = Venue.query.get(venue_id)
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.image_link = form.image_link.data
            venue.facebook_link = form.facebook_link.data
            venue.website = form.website.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            venue.genres = ",".join(form.genres.data)

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
                website=form.website_link.data,
                genres=",".join(form.genres.data),
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data,
            )
            db.session.add(created_artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')

        except Exception:
            db.session.rollback()
            flash(" Artist " + request.form['name'] + "could not be listed.")
        finally:
            db.session.close()
    else:
        print(form.errors)
        flash(" Artist could not be validated.")

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = []
    for i in Show.query.all():
        data.append({
            "venue_id": i.venue_id,
            "venue_name": Venue.query.filter_by(id=i.venue_id).first().name,
            "artist_id": i.artist_id,
            "artist_name": Artist.query.filter_by(id=i.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(id=i.artist_id).first().image_link,
            "start_time": i.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)

    if form.validate():
        new_show = Show(
            venue_id=request.form['venue_id'],
            artist_id=request.form['artist_id'],
            start_time=request.form['start_time'],
        )

        try:
            db.session.add(new_show)
            db.session.commit()
            flash('Show ' + {new_show.name} + ' was successfully listed!')

        except Exception as e:
            db.session.rollback()
            print(sys.exc_info())
            flash(f'An error occurred. Show couldn\'t be created')
        finally:
            db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404
    

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

@app.errorhandler(400)
def bad_request(error):
    return render_template('errors/400.html'), 400

@app.errorhandler(401)
def unauthorized(error):
    return render_template('errors/401.html'), 401

@app.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(422)
def not_processable(error):
    return render_template('errors/422.html'), 422

@app.errorhandler(405)
def invalid_method(error):
    return render_template('errors/405.html'), 405

@app.errorhandler(409)
def duplicate_resource(error):
    return render_template('errors/409.html'), 409




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
