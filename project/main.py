import os
from flask import Flask, render_template, request, escape, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, current_user, login_required, UserMixin


csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    csrf.init_app(app)
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    return app


app = create_app()
app.config['SECRET_KEY'] = '132rqdvwo243846590thtkne,bex/zdejfut5tu8530'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.Login'
login_manager.init_app(app)


class User(UserMixin, db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    forums = db.relationship('Forum', lazy='dynamic')

    def __str__(self):
        return self.login


class Forum(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')

    def __str__(self):
        return self.title


db.create_all()
db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/main')
def Main():
    forums = Forum.query.order_by(Forum.id).all()
    return render_template('main.html', forums=forums, user=current_user)


@app.route('/create', methods=['POST','GET'])
@login_required
def create():
    if request.method == 'POST':
        new_title = escape(request.form['title'])
        new_text = escape(request.form['text'])
        new_forum = Forum()
        new_forum.title = new_title
        new_forum.text = new_text
        new_forum.user_id = current_user.id
        try:
            db.session.add(new_forum)
            db.session.commit()
            return redirect(url_for('Main'))
        except:
            return 'DB record error'
    else:
        return render_template('create.html')


@app.route('/update/<int:id>', methods=['POST', 'GET'])
@login_required
def update(id):
    if request.method == 'POST':
        updated_forum = Forum.query.get_or_404(id)
        new_title = escape(request.form['title'])
        new_text = escape(request.form['text'])
        try:
            updated_forum.title = new_title
            updated_forum.text = new_text
            db.session.commit()
            return redirect(url_for('Main'))
        except:
            return 'Updating error!!'
    else:
        updated_forum = Forum.query.get_or_404(id)
        return render_template('update.html', context=updated_forum)


@app.route('/delete/<int:id>', methods=['POST', 'GET'])
@login_required
def delete(id):
    obj = Forum.query.get_or_404(id)
    if request.method == 'POST':
        try:
            db.session.delete(obj)
            db.session.commit()
            return redirect(url_for('Main'))
        except:
            return "Error with deleting the item"
    else:
        return render_template('delete.html', obj=obj)


if __name__ == '__main__':
    app.run(debug=True)
