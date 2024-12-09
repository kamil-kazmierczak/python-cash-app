from flask import render_template, redirect, url_for, Flask, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from models.entities import init_entities, User, Asset, Price, db
from services.price_service import PriceService
from services.file_service import FileService
from models.entities import find_last_price, find_user
from services.currency_service import CurrencyService, Currency

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kamil'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
init_entities(app)


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
    try:
        CurrencyService.save_currency_rate(Currency.USD, Currency.PLN)
    except IntegrityError as e:
        db.session.rollback()
        print(str(e))

    usd = PriceService.fetch_usd_price_in_pln()
    usd_price = Price(asset_id=Asset.query.filter_by(name='USD').first().id, value=usd.value, date=usd.date_)
    if usd_price:
        try:
            db.session.add(usd_price)
            db.session.commit()
            print(f"USD price added: {usd_price.value} for {usd_price.date}")
        except IntegrityError as e:
            db.session.rollback()
            print(str(e))
    else:
        print("USD price not saved!")

    btc = PriceService.fetch_crypto_price_in_usd('BTC')
    btc_price = Price(asset_id=Asset.query.filter_by(name='BTC').first().id, value=btc.value, date=btc.date_)
    if btc_price:
        try:
            db.session.add(btc_price)
            db.session.commit()
            print(f"BTC price added: {btc_price.value} for {btc_price.date}")
        except IntegrityError as e:
            db.session.rollback()
            print(str(e))
    else:
        print("BTC price not saved!")

    eth = PriceService.fetch_crypto_price_in_usd('ETH')
    eth_price = Price(asset_id=Asset.query.filter_by(name='ETH').first().id, value=eth.value, date=eth.date_)
    if eth_price:
        try:
            db.session.add(eth_price)
            db.session.commit()
            print(f"ETH price added: {eth_price.value} for {eth_price.date}")
        except IntegrityError as e:
            db.session.rollback()
            print(str(e))
    else:
        print("ETH price not saved!")

    dot = PriceService.fetch_crypto_price_in_usd('DOT')
    dot_price = Price(asset_id=Asset.query.filter_by(name='DOT').first().id, value=dot.value, date=dot.date_)
    if dot_price:
        try:
            db.session.add(dot_price)
            db.session.commit()
            print(f"DOT price added: {dot_price.value} for {dot_price.date}")
        except IntegrityError as e:
            db.session.rollback()
            print(str(e))
    else:
        print("DOT price not saved!")

    vuaa = PriceService.fetch_vuaa_price_in_usd()
    vuaa_price = Price(asset_id=Asset.query.filter_by(name='VUAA.UK').first().id, value=vuaa.value, date=vuaa.date_)
    if vuaa_price:
        try:
            db.session.add(vuaa_price)
            db.session.commit()
            print(f"VUAA price added: {vuaa_price.value} for {vuaa_price.date}")
        except IntegrityError as e:
            db.session.rollback()
            print(str(e))
    else:
        print("VUAA price not saved!")

    gold = PriceService.fetch_gold_one_oz_coin_price_in_pln()
    gold_price = Price(asset_id=Asset.query.filter_by(name='GOLD').first().id, value=gold.value, date=gold.date_)
    if gold_price:
        try:
            db.session.add(gold_price)
            db.session.commit()
            print(f"Gold price added: {gold_price.value} for {gold_price.date}")
        except IntegrityError as e:
            db.session.rollback()
            print(str(e))
    else:
        print("Gold price not saved!")

    # FileService.save_json(json_usd, 'json/usd.json')
    # FileService.save_json(json_btc, 'json/btc.json')
    # FileService.save_json(json_eth, 'json/eth.json')
    # FileService.save_json(json_dot, 'json/dot.json')
    # FileService.save_json(json_vuaa, 'json/vuaa.json')
    # FileService.save_json(json_gold, 'json/gold.json')

    flash('Download data successful.', 'success')
    print("Jsons saved")
    return {}


@app.route('/assets')
@login_required
def assets():
    assets_per_name = FileService.read_assets()

    prices = [
        find_last_price('BTC'),
        find_last_price('ETH'),
        find_last_price('DOT'),
        find_last_price('VUAA.UK'),
        find_last_price('NBP'),
        find_last_price('USD'),
        find_last_price('GOLD')
    ]

    user_portfolio = find_user('kamilp').portfolios

    return render_template('assets.html',
                           title='Money Portfolio',
                           username='Kamil',
                           prices=prices,
                           user_portfolio=user_portfolio,
                           assets_per_name=assets_per_name
                           )


if __name__ == '__main__':
    app.run(debug=True)
