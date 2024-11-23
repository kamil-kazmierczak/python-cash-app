from flask import render_template, redirect, url_for, Flask, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from sqlalchemy.orm import Session
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from models.users import init_users, User, db
from services.price_service import PriceService
from services.file_service import FileService

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

    FileService.save_json(json_usd, 'json/usd.json')
    FileService.save_json(json_btc, 'json/btc.json')
    FileService.save_json(json_eth, 'json/eth.json')
    FileService.save_json(json_dot, 'json/dot.json')
    FileService.save_json(json_vuaa, 'json/vuaa.json')
    print("Jsons saved")
    return json_usd


@app.route('/assets')
@login_required
def assets():
    btc_price = round(float(FileService.read_btc_price("2024-11-23")), 2)
    eth_price = round(float(FileService.read_eth_price("2024-11-23")), 2)
    dot_price = round(float(FileService.read_dot_price("2024-11-23")), 2)
    vuaa_price = round(float(FileService.read_vuaa_price("2024-11-22")), 2)
    nbp_price = 100
    usd = round(float(FileService.read_usd_price_in_pln()), 2)

    assets_per_name = FileService.read_assets()

    value_btc_pln = round(float(assets_per_name['BTC']) * float(btc_price) * usd, 2)
    value_eth_pln = round(float(assets_per_name['ETH']) * float(eth_price) * usd, 2)
    value_dot_pln = round(float(assets_per_name['DOT']) * float(dot_price) * usd, 2)
    value_vuaa_pln = round(float(assets_per_name['VUAA.UK']) * float(vuaa_price) * usd, 2)
    value_nbp_pln = assets_per_name['NBP'] * nbp_price
    value_usd_pln = round(assets_per_name['USD'] * usd, 2)

    _sum = round(value_btc_pln + value_eth_pln + value_dot_pln + value_vuaa_pln + value_nbp_pln + value_usd_pln, 2)

    overall = {
        'BTC': round(value_btc_pln / _sum, 2) * 100,
        'ETH': round(value_eth_pln / _sum, 2) * 100,
        'DOT': round(value_dot_pln / _sum, 2) * 100,
        'VUAA.UK': round(value_vuaa_pln / _sum, 2) * 100,
        'NBP': round(value_nbp_pln / _sum, 2) * 100,
        'USD': round(value_usd_pln / _sum, 2) * 100
    }

    return render_template('assets.html',
                           title='Money Portfolio',
                           username='Kamil',
                           btc_price=btc_price,
                           eth_price=eth_price,
                           dot_price=dot_price,
                           vuaa_price=vuaa_price,
                           usd_price=usd,
                           nbp_price=nbp_price,
                           value_btc_pln=value_btc_pln,
                           value_eth_pln=value_eth_pln,
                           value_dot_pln=value_dot_pln,
                           value_vuaa_pln=value_vuaa_pln,
                           value_nbp_pln=value_nbp_pln,
                           value_usd_pln=value_usd_pln,
                           assets_per_name=assets_per_name,
                           overall=overall,
                           _sum=_sum
                           )


if __name__ == '__main__':
    app.run(debug=True)
