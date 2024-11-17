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


@app.route('/assets')
@login_required
def assets():
    btc_price = FileService.read_btc_price("2024-11-17")
    eth_price = FileService.read_eth_price("2024-11-17")
    dot_price = FileService.read_dot_price("2024-11-17")
    vuaa_price = FileService.read_vuaa_price("2024-11-15")
    usd = FileService.read_usd_price_in_pln()
    assets_per_name = FileService.read_assets()
    print(assets_per_name)

    return render_template('assets.html',
                           title='Money Portfolio',
                           username='Kamil',
                           btcPrice=btc_price,
                           ethPrice=eth_price,
                           dotPrice=dot_price,
                           vuaaPrice=vuaa_price,
                           usdPrice=usd
                           )


if __name__ == '__main__':
    app.run(debug=True)