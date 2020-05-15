#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#import datetime
from sqlalchemy import ARRAY, String
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database - DONE

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    #added - DONE
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    show = db.relationship("Show", back_populates="venue")

    # TODO: implement any missing fields, as a database migration using
    # Flask-Migrate - DONE
    def venue_to_dictionary(self):
        return{
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'genres': self.genres,
            'website': self.website,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description
        }


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    #added - DONE
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    show = db.relationship('Show', back_populates="artist")

    # TODO: implement any missing fields, as a database migration using
    # Flask-Migrate - DONE
    def artist_to_dictionary(self):
        return{
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'genres': self.genres,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'website': self.website,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description
        }

# TODO Implement Show and Artist models, and complete all model
# relationships and properties, as a database migration. - DONE


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_time = db.Column(db.DateTime)
    # table linked to venue via db.relationship
    venue_id = db.Column(
        db.Integer,
        db.ForeignKey('venue.id'),
        primary_key=True)
    # table linked to artist via db.relationship
    artist_id = db.Column(
        db.Integer,
        db.ForeignKey('artist.id'),
        primary_key=True)
    venue = db.relationship("Venue", back_populates="show")
    artist = db.relationship("Artist", back_populates="show")

    def show_artist(self):
        return {
            'artist_id': self.artist_id,
            'artist_name': self.artist.name,
            'artist_image_link': self.artist.image_link,
            'start_time': self.start_time
        }

    def show_venue(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.venue.name,
            'venue_image_link': self.venue.image_link,
            'start_time': self.start_time
        }


# used a db.create all because the migration fuction wasn't recognising
# the autoincrement=True change on the shows db
db.create_all()


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


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
    # TODO: replace with real venues data. - DONE
    # num_shows should be aggregated based on number of upcoming shows per
    # venue.

    data = []

    try:

        venues = Venue.query.order_by(Venue.city).all()
        data = []

        for venue in venues:
            data.append({
                "city": venue.city,
                "state": venue.state,
                "venues": [{
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": Show.query.filter(Show.venue_id == venue.id).count(),
                }]
            })

    except BaseException:
        db.session.rollback()

    finally:
        db.session.close()

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. - DONE
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live
    # Music & Coffee"

    # .ilike provides case-insensitive search
    search_term = request.form.get('search_term')
    search_results = Venue.query.filter(Venue.name.ilike('%{}%'.format(
        search_term))).all()  # searches matching items from search form

    response = {}
    response['count'] = len(search_results)
    response['data'] = search_results

    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    # - DONE
    venue = Venue.query.filter(Venue.id == venue_id).first()
    past_shows_query = Show.query.join(Artist).filter(
        Show.venue_id == venue_id).filter(
        Show.start_time < datetime.now()).all()
    past_shows = []

    for show in past_shows_query:
        past_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    upcoming_shows_query = Show.query.join(Artist).filter(
        Show.venue_id == venue_id).filter(
        Show.start_time >= datetime.now()).all()
    upcoming_shows = []

    for show in upcoming_shows_query:
        upcoming_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    data = venue.venue_to_dictionary()
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead - DONE
    venue_form = VenueForm(request.form)

    venue = Venue(
        name=venue_form.name.data,
        city=venue_form.city.data,
        state=venue_form.state.data,
        address=venue_form.address.data,
        phone=venue_form.phone.data,
        image_link="https://images.unsplash.com/photo-1537151608828-ea2b11777ee8?ixlib=rb-1.2.1&q=80&fm=jpg&crop=entropy&cs=tinysrgb&w=1080&fit=max&ixid=eyJhcHBfaWQiOjF9",
        genres=request.form.getlist('genres'),
        facebook_link=venue_form.facebook_link.data,
    )
    # TODO: modify data to be the data object returned from db insertion - DONE
    # check if venue has already been listed by checking the name
    # on successful db insert, flash success
    # flash('Venue ' + request.form['name'] + ' was successfully listed!')
    try:
        number = Venue.query.filter(Venue.name == venue.name).count()

        if number == 0:
            db.session.add(venue)
            db.session.commit()
            flash(
                'Venue ' +
                request.form['name'] +
                ' was successfully listed!')
        else:
            flash(
                'Venue ' +
                request.form['name'] +
                ' is already listed, please try again!')

    # TODO: on unsuccessful db insert, flash an error instead. - DONE
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    except BaseException:
        db.session.rollback()
        print('DB ROLLBACK')
        print(sys.exc_info())
        flash(
            'An error occured. Venue ' +
            request.form['name'] +
            ' could not be listed.')
    finally:
        print('DB CLOSED')
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using - DONE
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit
    # could fail.

    venue = Venue.query.get(venue_id)

    try:
        Show.query.filter(Show.venue_id == venue.id).delete()
        db.session.delete(venue)
        db.session.commit()

    except BaseException:
        db.session.rollback()

    finally:
        db.session.close()

    return render_template('pages/home.html')

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the
    # homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database - DONE
    artists = Artist.query.order_by(Artist.city).all()
    data = []

    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name,
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. - DONE
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term')
    search_results = Artist.query.filter(Artist.name.ilike('%{}%'.format(
        search_term))).all()  # searches matching items from search form

    response = {}
    response['count'] = len(search_results)
    response['data'] = search_results

    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    # - DONE
    artist = Artist.query.filter(Artist.id == artist_id).first()

    past_shows_query = Show.query.join(Venue).filter(
        Show.artist_id == artist_id).filter(
        Show.start_time < datetime.now()).all()
    past_shows = []

    for show in past_shows_query:
        past_shows.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    upcoming_shows_query = Show.query.join(Venue).filter(
        Show.artist_id == artist_id).filter(
        Show.start_time >= datetime.now()).all()
    upcoming_shows = []

    for show in upcoming_shows_query:
        upcoming_shows.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    data = artist.artist_to_dictionary()
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # TODO: populate form with fields from artist with ID <artist_id> - DONE
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing - DONE
    # artist record with ID <artist_id> using the new attributes

    form_artist = ArtistForm(request.form)

    try:
        artist = Artist.query.get(artist_id)

        artist.name = form_artist.name.data
        artist.genres = ", ".join(form_artist.genres.data)
        artist.city = form_artist.city.data
        artist.state = form_artist.state.data
        artist.phone = form_artist.phone.data
        artist.facebook_link = form_artist.facebook_link.data

        db.session.commit()

    except BaseException:
        db.session.rollback()
        print('DB ROLLBACK')
        print(sys.exc_info())
        flash(f'Problem updating artist, please try again!')

    finally:
        print('DB CLOSED')
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # TODO: populate form with values from venue with ID <venue_id> - DONE
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing - DONE
    # venue record with ID <venue_id> using the new attributes
    form_venue = VenueForm(request.form)

    try:
        venue = Venue.query.get(venue_id)

        venue.name = form_venue.name.data
        venue.genres = ", ".join(form_venue.genres.data)
        venue.address = form_venue.address.data
        venue.city = form_venue.city.data
        venue.state = form_venue.state.data
        venue.phone = form_venue.phone.data
        venue.facebook_link = form_venue.facebook_link.data

        db.session.commit()
    except BaseException:
        db.session.rollback()
        print('DB rollback')
        print(sys.exc_info())
        flash(f'There was a problem updating the Venue, please try again')
    finally:
        print('db closed')
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead - DONE
    artist_form = VenueForm(request.form)

    artist = Artist(
        name=request.form['name'],
        city=request.form['city'],
        state=request.form['state'],
        phone=request.form['phone'],
        image_link="https://images.unsplash.com/photo-1537151608828-ea2b11777ee8?ixlib=rb-1.2.1&q=80&fm=jpg&crop=entropy&cs=tinysrgb&w=1080&fit=max&ixid=eyJhcHBfaWQiOjF9",
        genres=request.form.getlist('genres'),
        facebook_link=request.form['facebook_link'],

    )
    # TODO: modify data to be the data object returned from db insertion - DONE
    try:
        number = Artist.query.filter(Artist.name == artist.name).count()

        if number == 0:
            db.session.add(artist)
            db.session.commit()
            # on successful db insert, flash success
            flash(
                'Artist ' +
                request.form['name'] +
                ' was successfully listed!')
        else:
            flash(
                'Artist ' +
                request.form['name'] +
                ' is already listed, try again!')

    except BaseException:
        db.session.rollback()
        print('DB ROLLBACK')
        print(sys.exc_info())
        # TODO: on unsuccessful db insert, flash an error instead. - DONE
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be
        # listed.')
        flash('There was a problem recording the artist ' +
              request.form['name'] + ' please try again!')

    finally:
        print('DB CLOSED')
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data. DONE
    # num_shows should be aggregated based on number of upcoming shows per
    # venue.
    show = Show.query.all()

    data = []

    for result in show:
        venue = Venue.query.get(result.venue_id)
        artist = Artist.query.get(result.artist_id)
        print(result.start_time)
        data.append({
            "venue_id": result.venue_id,
            "venue_name": venue.name,
            "artist_id": result.artist_id,
            "artist_name": artist.name,
            "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
            "start_time": (result.start_time).strftime("%m/%d/%Y, %H:%M")
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
    # TODO: insert form data as a new Show record in the db, instead - DONE

    show_form = ShowForm(request.form)

    show = Show(
        artist_id=show_form.artist_id.data,
        venue_id=show_form.venue_id.data,
        start_time=show_form.start_time.data,
    )

    try:
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except BaseException:
        db.session.rollback()
        print('DB ROLLBACK')
        print(sys.exc_info())
        # TODO: on unsuccessful db insert, flash an error instead. - DONE
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Show could not be listed.')
    finally:
        print('DB CLOSE')
        db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
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
