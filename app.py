#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
        Flask,
        render_template,
        request,
        Response,
        flash,
        redirect,
        url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
from flask_migrate import Migrate
import sys
from array import array

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# ------------ Controllers ------------------- #
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

# ----------------------------------------------------------------- #
# -------------- Venues -------------------- #
#  ---------------------------------------------------------------- #

@app.route('/venues')
def venues():
  # num_shows should be aggregated based on number of upcoming shows per venue.
  data = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  result= []
  for venue_data in data:
      city_name=venue_data[0]
      city_state=venue_data[1]
      que = db.session.query(Venue).filter(Venue.city == city_name, Venue.state == city_state)
      group = {
      "city": city_name,
      "state": city_state,
      "venues": []
      }
      venues = que.all()
      for venue in venues:
          print(venue.id)
          group['venues'].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": Venue.query.filter_by(id=venue.id).join(Show).count()
          })
      result.append(group)

  return render_template('pages/venues.html', areas=result);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # search for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  """
  Searches for a Venue according to any letter input
  (Using ilike to make it case insensitive)
  for loop in order to list items through a listed view.
  """
  search_venue = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_venue))).all()
  data = []
  for venue in venues:
      keep = {}
      keep['id'] = venue.id
      keep['name'] = venue.name
      keep['num_upcoming_shows'] = venue.shows.count()
      data.append(keep)

  response = {}
  response['count'] = len(data)
  response['data'] = data

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  """
  The code below combines the model for Show with Venues & Artist in order
  to locate all the necessary data required in order to show the past shows
  and upcoming showing through comparing the time right now (datetime.now())
  and the date of the show.
  if the start time is previous to the time right now it would show appropriate
  shows accordingly. Moreover, it provides a view to an individual Venue on its
  dedicated page.

  """
  time_atm = datetime.now()
  my_venues = Venue.query.get(venue_id)
  setattr(my_venues, 'past_shows', [])
  setattr(my_venues, 'upcoming_shows', [])
  num_past_shows = 0
  num_upcoming_shows = 0
  try:
    shows = db.session.query(Artist, Show.start_time).join(Show).filter(Show.venue_id == venue_id)
    for artist, start_time in shows:
        if start_time < time_atm:
            my_venues.past_shows.append({
              'venue_id' : venue.id,
              'venue_name' : venue.name,
              'venue_image_link' : venue.image_link,
              'start_time' : str(start_time)
              })
            num_past_shows += 1
        else:
            my_venues.upcoming_shows.append({
                'venue_id' : venue.id,
                'venue_name' : venue.name,
                'venue_image_link' : venue.image_link,
                'start_time' : str(start_time)
                })
            num_upcoming_shows += 1
    setattr(my_venues, 'num_past_shows', num_past_shows)
    setattr(my_venues, 'num_upcoming_shows', num_upcoming_shows)
  except Exception:
    error = True
    print(sys.exc_info())
  return render_template('pages/show_venue.html', venue=my_venues)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    # on successful db insert, flash success
    # flash('Venue ' + request.form['name'] + ' was successfully listed!')
    """
    Retrieves the form data submitted through the new_venue.html file and submits
    the information onto the database. Collecting each input bar at a time then
    committing it to the database.
    in case of an error - requested to raise an Exception.

    """
    form = VenueForm()
    data = {}                           # Set container standard
    data['name'] = form.name.data       # comply my standard
    try:                                # then interact with each form item.
        new_venue = Venue(
        name=form.name.data,
        genres=form.genres.data,
        address=form.address.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        website=form.website.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data
        )
        db.session.add(new_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')

            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  """
  Lets users click on the button in the Specified venue page to delete the venue
  once filtered by the ID of the venue in mind it commits the delete() venue

  """
  error = False
  try:
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
      flash('The Venue has been deleted successfully!')
  except Exception:
      error = False
      print(sys.exc_info())
      db.session.rollback()
      flash('Venue could not be deleted, please try again.')
  finally:
      db.session.close()
  return render_template('pages/home.html')

# -----------------------------------------------------------------
#  ---------- Artists -------------
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  try:
      data = db.session.query(Artist.id, Artist.name).group_by(Artist.id, Artist.name).all()
      result = []
      for artist_data in data:
          artist_names=artist_data[0]
          artist_ids=artist_data[1]
          que = db.session.query(Artist).filter(Artist.id == artist_ids, Artist.name == artist_names)
          grouping = {
            "id": artist_ids,
            "name": artist_names,
            }
      result.append(grouping)
  except Exception:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Artist\'s could not be found.')
  finally:
      db.session.close()
      print(data)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band
    """
    Searches for an Artist according to any letter input
    (Using ilike to make it case insensitive)
    for loop in order to list items through a listed view.
    """

    search_artist = request.form.get('search_term')
    s_artist = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_artist))).all()
    data = []
    for artist in s_artist:
        keep_ar = {}
        keep_ar['id'] = artist.id
        keep_ar['name'] = artist.name
        keep_ar['num_upcoming_shows'] = len(artist.shows)
        data.append(keep_ar)

    response = {}
    response['count'] = len(data)
    response['data'] = data
    return render_template('pages/search_artists.html', results=response, search_artist=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  """
  The code below combines the model for Show with Venues & Artist in order
  to locate all the necessary data required in order to show the past shows
  and upcoming showing through comparing the time right now (datetime.now())
  and the date of the show.
  if the start time is previous to the time right now it would show appropriate
  shows accordingly. Moreover, it provides a view to an individual Venue on its
  dedicated page.

  """
  time_atm = datetime.now()
  my_artists = Artist.query.get(artist_id)
  setattr(my_artists, 'past_shows', [])
  setattr(my_artists, 'upcoming_shows', [])
  num_past_shows = 0
  num_upcoming_shows = 0
  try:
      shows = db.session.query(Venue, Show.start_time).join(Show).filter(Show.artist_id == artist_id)
      for venue, start_time in shows:
        if start_time < time_atm:
            my_artists.past_shows.append({
                'venue_id': venue.id,
                'venue_name': venue.name,
                'venue_image_link': venue.image_link,
                'start_time': str(start_time)
                })
            num_past_shows += 1
        else:
            my_artists.upcoming_shows.append({
                'venue_id': venue.id,
                'venue_name': venue.name,
                'venue_image_link': venue.image_link,
                'start_time': str(start_time)
                })
            num_upcoming_shows += 1
      setattr(my_artists, 'num_past_shows', num_past_shows)
      setattr(my_artists, 'num_upcoming_shows', num_upcoming_shows)
  except Exception:
      error = True
      print(sys.exc_info())
      flash('Artist Could not be found.')
  return render_template('pages/show_artist.html', artist=my_artists)

# http://pytz.sourceforge.net/

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    """
    Retrieves previously input data from the Artist information
    Which is available.

    """
    artist = Artist.query.get(artist_id)
    form = ArtistForm(
    name = artist.name,
    city = artist.city,
    state= artist.state,
    phone= artist.phone,
    genres = artist.genres,
    facebook_link = artist.facebook_link,
    image_link = artist.image_link,
    website = artist.website,
    seeking_venue = artist.seeking_venue,
    seeking_description = artist.seeking_description
    )
  # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  """
  Supports an edit option for a previously submitted form for the specified
  Artist.

  """
  error = False
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  try:
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.website = form.website.data
    artist.image_link = form.image_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' has been updated.')
  except Exception:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
        flash('An error has occurred. Artist ' + request.form['name'] + ' couldn\'t be updated, please try again.')
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
      """
      Retrieves previously input data from the Venue information
      Which is available.

      """
      venue = Venue.query.get(venue_id)
      form = VenueForm(
          name = venue.name,
          city = venue.city,
          state = venue.state,
          phone = venue.phone,
          genres = venue.genres,
          facebook_link = venue.facebook_link,
          website = venue.website,
          address = venue.address,
          image_link = venue.image_link,
          seeking_talent = venue.seeking_talent,
          seeking_description = venue.seeking_description,
        )
      return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  """
  Supports an edit option for a previously submitted form for the specified
  Venue.

  """
  error = False
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  try:
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.address = form.address.data
    venue.website = form.website.data
    venue.image_link = form.image_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.add(venue)
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()
    if error:
        flash('An error has occurred. Venue ' + request.form['name'] + ' couldn\'t be updated, please try again.')
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    else:
        flash('Venue ' + form.name.data + ' has been updated.')
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    """
    Retrieves the form data submitted through the new_artist.html file and submits
    the information onto the database. Collecting each input bar at a time then
    committing it to the database.
    in case of an error - requested to raise an Exception.

    """
    form = ArtistForm()
    data = {}                        # Set container standard
    data['name'] = form.name.data    # comply my standard
    try:                             # then interact with each form item.
        new_artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        genres=",".join(form.genres.data),
        website=form.website.data,
        image_link=form.image_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data,
        facebook_link=form.facebook_link.data
        )
        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except Exception:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

# -----------------------------------------------------------------
# ------------- Shows ---------------
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  """
  Combines the Models (Artist, Venue, Show) data in order to provide a shared
  model of the shows between an Artist and a Venue which the artist performs
  at. Taking one data point at a time
  (*show_venue_id=shows_data[0] taking ID of specified model)

  """
  data = db.session.query(Show.venue_id, Venue.name, Show.artist_id, Artist.name, Artist.image_link, Show.start_time).join(Venue).join(Artist).group_by(Show.venue_id, Venue.name, Show.artist_id, Artist.name, Artist.image_link, Show.start_time).all()
  result = []
  for shows_data in data:
    show_venue_id=shows_data[0]
    show_venue_name=shows_data[1]
    show_artist_id=shows_data[2]
    show_artist_name=shows_data[3]
    show_artist_image_link=shows_data[4]
    show_start_time=shows_data[5]
    que = db.session.query(Show).filter(Show.venue_id == show_venue_id, Venue.name == show_venue_name, Show.artist_id == show_artist_id, Artist.name == show_artist_name, Artist.image_link == show_artist_image_link, Show.start_time == show_start_time)
    groupings = {
    "venue_id": show_venue_id,
    "venue_name": show_venue_name,
    "artist_id": show_artist_id,
    "artist_name": show_artist_name,
    "artist_image_link": show_artist_image_link,
    "start_time": str(show_start_time)
    }
    result.append(groupings)

  return render_template('pages/shows.html', shows=result)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  """
  Retrieves the form data submitted through the new_show.html file and submits
  the information onto the database. Collecting each input bar at a time then
  committing it to the database.
  in case of an error - requested to raise an Exception.

  """
  form = ShowForm(request.form)
  try:
    new_show = Show(
      artist_id=request.form['artist_id'],
      venue_id=request.form['venue_id'],
      start_time=request.form['start_time']
      )
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except Exception:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
