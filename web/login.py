
from flask_login import LoginManager, UserMixin
from .models import User

login_manager = LoginManager()
login_manager.login_view = 'views.login'

class UserLogin(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
