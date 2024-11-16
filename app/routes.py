from flask import Blueprint, flash, request, jsonify, render_template, redirect, send_file, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from .models import User, Event, Booking
from .utils import check_email, check_password
from . import db
from datetime import date, datetime, timedelta
import math

main = Blueprint('main', __name__)
@main.context_processor
def inject():
    if current_user.is_authenticated:
        return {'current_user': current_user}
    return {'current_user': None}

@main.app_errorhandler(404)
def PageNotFound(e):
    return render_template("error.html", error_code=404, error_message="The page you're looking for doesn't exist."), 404
@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template("error.html", error_code=500, error_message="Internal Server Error. Please try again later."), 500
@main.app_errorhandler(403)
def forbidden(e):
    return render_template("error.html", error_code=403, error_message="Access denied. You do not have the necessary permissions to access this page."), 403

''' ROUTE '''
@main.route('/', methods=["GET"])
def welcome():
    events = Event.query.order_by(Event.event_data.desc()).limit(3).all()
    return render_template('welcome.html', events=events)

@main.route('/about', methods=["GET"])
def about():
    return render_template('about.html')

@main.route('/location', methods=["GET"])
def location():
    return render_template('location.html')

@main.route('/contact', methods=["GET"])
def contact():
    return render_template('contact.html')

@main.route('/privacy-policy', methods=["GET"])
def policy():
    return render_template('policy.html')

@main.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    name = request.form.get('name')
    genre = request.form.get('genre')
    email = request.form.get('email')
    is_valid, error_message = check_email(email)
    if not is_valid:
        flash(error_message, 'danger')
        return redirect(url_for('main.signup'))
    
    password = request.form.get('password')
    is_valid, error_message = check_password(password)
    if not is_valid:
        flash(error_message, 'danger')
        return redirect(url_for('main.signup'))
    password = generate_password_hash(password)    
    role = request.form.get('role')

    user = User(name=name, genre=genre, email=email, password=password, role=role)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('main.welcome'))

@main.route('/signin', methods=["GET", "POST"])
def signin():
    if request.method == 'GET':
        return render_template('signin.html')
    
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return redirect(url_for('main.welcome'))
    
@main.route('/signout')
def signout():
    logout_user()
    return redirect(url_for('main.welcome'))

@main.route('/user/<int:id>', methods=["GET"])
@login_required
def profile(id):
    user = db.session.get(User, id)    
    if not user:
        return render_template('error.html', error_message="L'utente richiesto non è stato trovato.")
    '''   
    mbook = ""
       
    if not Booking.query.filter_by(user_id=user.id).all():
        mbook = "Non hai ancora effettuato prenotazioni.<br><br>Erplora gli eventi disponibili e prenota subito per approfittare delle offerte speciali!"

    bookings = Booking.query.filter_by(user_id=user.id).all()
    return render_template('uprofile.html', user=user, booKings=bookings, mbook=mbook)
    '''
    return render_template('profile.html', user=user)

@main.route('/event', methods=["GET"])
@login_required
def event():
    events = Event.query.all()
    return render_template('event.html', events=events)

@main.route('/emanager', methods=["GET"])
@login_required
def emanager():
    events = Event.query.all()
    return render_template('emanager.html', events=events)

@main.route('/event/create', methods=["GET", "POST"])
@login_required
def ecreate():
    if request.method == 'GET':
        return render_template('ecreate.html')
    
    event = Event(
        title = request.form['title'],
        description = request.form['description'],
        event_data = request.form['event_data'],
        place = request.form['place']
    )

    db.session.add(event)
    db.session.commit()        
    return redirect(url_for('main.emanager'))   

@main.route('/event/<int:id>/edit', methods=["GET", "POST"])
@login_required
def eedit(id):
    event = Event.query.get(id)
    if not event:
        return render_template('error.html', error_message="L'evento richiesto non è stato trovato.")    
    
    if request.method == 'GET':
        return render_template('eedit.html', event=event)
    
    event.title = request.form['title']
    event.description = request.form['description']
    event.event_data = request.form['event_data']
    event.place = request.form['place']

    db.session.commit()
    return redirect(url_for('main.emanager'))
    
@main.route('/event/<int:id>/drop', methods=["POST"])
@login_required
def edrop(id):
    event = Event.query.get(id)
    if not event:
        return render_template('error.html', error_message="L'evento richiesto non è stato trovato.") 
    
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('main.emanager'))
