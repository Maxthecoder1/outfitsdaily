import requests
from flask import Flask, render_template, request, flash, redirect, g, url_for, Markup
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
import os
from flask_sqlalchemy import SQLAlchemy
import pygeoip
gi = pygeoip.GeoIP('GeoLiteCity.dat') # remoteipadress
from WeatherAPIXU import WeatherAPIXU
wa = WeatherAPIXU.Weather_APIXU(api_key='1c4e1ac423bd46fc987213126170512')   #apikey


def wsort(forecast, query):
    weather = []
    weather.append(query)
    weather.append(forecast['forecast']['forecastday'][0]['date'])
    weather.append(forecast['forecast']['forecastday'][0]['day']['condition']['text'])
    weather.append(forecast['forecast']['forecastday'][0]['day']['maxtemp_f'])
    weather.append(forecast['forecast']['forecastday'][0]['day']['maxtemp_c'])
    weather.append(forecast['forecast']['forecastday'][0]['day']['mintemp_f'])
    weather.append(forecast['forecast']['forecastday'][0]['day']['mintemp_c'])
    if 'snow' in forecast['forecast']['forecastday'][0]['day']['condition']['text'] or 'rain' in forecast['forecast']['forecastday'][0]['day']['condition']['text']:
        weather.append('1')
    else:
        weather.append('2')

        #heavy jacket
        #light jacket
        #rain jacket
        #hoodie
        #short sleeved shirt
        #long sleeved shirt
        #sweater
        #belt
        #pants, jeans, shorts, leggings, sweatpants
        #shoes,boots,sneakers
        #glasses
        #scarf
        #hat
        #images will store dictionary of ads {} use random.shuffle()
    return weather


def getweather(query=None, remoteaddr='64.233.161.99', gender='nonbinary'):
    if query is None:
        #turn remote addree into location city, state
        locquery = gi.record_by_addr(remoteaddr)
        query = '{0}, {1}'.format(locquery['city'], locquery['region_code'])
    try:
        forecast = wa.weather_forecast(query=query, days=str(1))
    except Exception as e:
        print(e)
        return 'Error: {0}'.format(e)
    else:
        return wsort(forecast, query)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "cuckoo"

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


#user -email, premium, admin
class User(db.Model):
    __tablename__ = "users"
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    username = db.Column('username', db.String(120))
    key_expiration = db.Column('key_expiration', db.DateTime)
    login_fails = db.Column('login_fails', db.Integer)
    account_lock_time = db.Column('account_lock_time', db.DateTime)
    usert = db.relationship("Ticket", backref="usert")

    @login_manager.user_loader
    def user_load(id):
        return User.query.get(id)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def __init__(self, username):
        self.username = username
        self.login_fails = 0


@app.before_request
def _before_request():
    g.user = current_user

# Index / search
@app.route('/', methods=['GET', 'POST']) #weather
def windex(): # query=None,gender='nonbinary'):
    error = None
    data = None
    if request.method == 'GET':
        a = getweather(remoteaddr='64.233.161.99', gender='nonbinary') #request.remote_addr
        if type(a) == 'str' and 'Error' in a:
            error = a
        return render_template('windex.html', data=a, error=error)
    if request.method == 'POST':
        location = request.form['location']
        print(location)
        a = getweather(query=location, remoteaddr=request.remote_addr, gender='nonbinary')
        if type(a) == 'str' and 'Error' in a:
            error = a
        return render_template('windex.html', data=a, error=error)


@app.route('/articles', methods=['GET']) #include search
def articles():
    error = None
    data = None
    return render_template('articles.html', data=data, error=error)

@app.route('/search', methods=['GET']) #include search
def search():
    error = None
    data = None
    return render_template('articles.html', data=data, error=error)

@app.route('/articles/url', methods=['GET'])
def indexe():
    error = None
    data = None
    return render_template('index.html', data=data, error=error)

@app.route('/contact', methods=['GET'])
def contact():
    error = None
    data = None
    return render_template('contact.html', data=data, error=error)

@app.route('/dmca', methods=['GET'])
def dmca():
    error = None
    data = None
    return render_template('dmca.html', data=data, error=error)

@app.route('/privacy', methods=['GET'])
def privacy():
    error = None
    data = None
    return render_template('privacy.html', data=data, error=error)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    error = None
    data = None
    return render_template('index.html', data=data, error=error)

@app.route('/newarticle', methods=['GET', 'POST'])
def newarticle():
    error = None
    data = None
    return render_template('index.html', data=data, error=error)

@app.route('/editarticle', methods=['GET', 'POST'])
def editarticle():
    error = None
    data = None
    return render_template('index.html', data=data, error=error)


@app.errorhandler(code_or_exception=404)
#make 404 get different image evry time from static 404 image folder
def page_not_found(e):
    return render_template('page_not_found.html'), 404


@app.errorhandler(500)
def internal_error(e):
    print(e)
    return render_template('500.html'), 500

#for templates cms use optional json using pattern: image1, word1, image2, word2,
#admin edit take user on get
#admin add take username and password on post

# Launch server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='localhost', port=port, threaded=True)