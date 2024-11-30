from flask import render_template, redirect, url_for, Flask, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from sqlalchemy.orm import Session
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from models.users import init_users, User, db
from services.price_service import PriceService
from services.file_service import FileService
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

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


@app.route('/download_data')
def download_data():
    json_usd = PriceService.fetch_usd_price_in_pln()
    json_btc = PriceService.fetch_crypto_price_in_usd('BTC')
    json_eth = PriceService.fetch_crypto_price_in_usd('ETH')
    json_dot = PriceService.fetch_crypto_price_in_usd('DOT')
    json_vuaa = PriceService.fetch_vuaa_price_in_usd()
    json_gold = PriceService.fetch_gold_one_oz_coin_price_in_pln()

    FileService.save_json(json_usd, 'json/usd.json')
    FileService.save_json(json_btc, 'json/btc.json')
    FileService.save_json(json_eth, 'json/eth.json')
    FileService.save_json(json_dot, 'json/dot.json')
    FileService.save_json(json_vuaa, 'json/vuaa.json')
    FileService.save_json(json_gold, 'json/gold.json')

    print("Jsons saved")
    return json_usd


@app.route('/assets')
@login_required
def assets():
    assets_per_name = FileService.read_assets()

    prices = {
        'BTC': round(float(FileService.read_current_crypto_price('json/btc.json')), 2),
        'ETH': round(float(FileService.read_current_crypto_price('json/eth.json')), 2),
        'DOT': round(float(FileService.read_current_crypto_price('json/dot.json')), 2),
        'VUAA.UK': round(float(FileService.read_current_etf_price('json/vuaa.json')), 2),
        'NBP': 100,
        'USD': round(float(FileService.read_usd_price_in_pln()), 2),
        'GOLD': float(FileService.read_gold_price_in_pln())
    }

    values = {
        'BTC': round(float(assets_per_name['BTC']) * prices['BTC'] * prices['USD'], 2),
        'ETH': round(float(assets_per_name['ETH']) * prices['ETH'] * prices['USD'], 2),
        'DOT': round(float(assets_per_name['DOT']) * prices['DOT'] * prices['USD'], 2),
        'VUAA.UK': round(float(assets_per_name['VUAA.UK']) * prices['VUAA.UK'] * prices['USD'], 2),
        'NBP': assets_per_name['NBP'] * prices['NBP'],
        'USD': round(assets_per_name['USD'] * prices['USD'], 2),
        'GOLD': round(assets_per_name['GOLD'] * prices['GOLD'], 2)
    }

    _sum = round(values['BTC'] + values['ETH'] + values['DOT'] + values['VUAA.UK'] + values['NBP'] + values['USD'] + values['GOLD'], 2)

    overall = {
        'BTC': f"{values['BTC'] / _sum * 100:.2f}",
        'ETH': f"{values['ETH'] / _sum * 100:.2f}",
        'DOT': f"{values['DOT'] / _sum * 100:.2f}",
        'VUAA.UK': f"{values['VUAA.UK'] / _sum * 100:.2f}",
        'NBP': f"{values['NBP'] / _sum * 100:.2f}",
        'USD': f"{values['USD'] / _sum * 100:.2f}",
        'GOLD': f"{values['GOLD'] / _sum * 100:.2f}"
    }

    return render_template('assets.html',
                           title='Money Portfolio',
                           username='Kamil',
                           prices=prices,
                           values=values,
                           assets_per_name=assets_per_name,
                           overall=overall,
                           _sum=_sum
                           )


if __name__ == '__main__':
    app.run(debug=True)
