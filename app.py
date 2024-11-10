from flask import render_template, redirect, url_for, Flask, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from sqlalchemy.orm import Session
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from models.users import init_users, User, db
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kamil'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
init_users(app)

@login_manager.user_loader
def load_user(user_id):
    with Session(db.engine) as session:
        return session.get(User, int(user_id))


@app.route('/')
@login_required
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return redirect(url_for('assets'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('assets'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            flash('Logged in successfully', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please login', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)





@app.route('/assets')
@login_required
def assets():
    usd = '4.03' #getCurrentUsdPriceInPln()
    vuaaPrice = '106' # getCurrentVuaaPriceInUsd()
    btcPrice = '76000' # getCurrentCryptoPriceInUsd("BTC")
    ethPrice = '3100' #getCurrentCryptoPriceInUsd("ETH")
    # dotPrice = getCurrentDotPriceInUsd()
    # goldPrice = getCurrentGoldPriceInUsd()

    return render_template('assets.html',
                           title='Money Portfolio',
                           username='Kamil',
                           usdPrice=usd,
                           btcPrice=btcPrice,
                           ethPrice=ethPrice,
                           vuaaPrice=vuaaPrice
                           )


def getCurrentUsdPriceInPln():
    api_key = 'fxr_live_d374de9d27c3038b38513faad079dcfe6026' # my free private api_key from fxrates
    url = 'https://api.fxratesapi.com/latest?api_key=' + api_key + '&currencies=PLN&base=USD'

    response = requests.request("GET", url)

    result = response.json()
    usdPrice = result['rates']['PLN']

    return usdPrice


def getCurrentCryptoPriceInUsd(cryptocurrencyTicker):
    api_key = 'IH2HAUUSGQSG69DT' # my free private api_key from alpha advantage
    url = 'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=' + cryptocurrencyTicker + '&market=USD&apikey=' + api_key

    price = requests.get(url).json()['Time Series (Digital Currency Daily)']['2024-11-08']['1. open']

    return price

def getCurrentVuaaPriceInUsd():
    api_key = 'IH2HAUUSGQSG69DT' # my free private api_key from alpha advantage
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=VUAA.LON&apikey=' + api_key

    priceVuaaUk = requests.get(url).json()['Time Series (Daily)']['2024-11-08']['1. open']

    return priceVuaaUk



if __name__ == '__main__':
    app.run(debug=True)
