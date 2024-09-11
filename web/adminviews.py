
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role.name == 'Admin'

class RoleAdmin(AdminModelView):
    column_list: tuple[str] = ('name', 'active')
    column_labels: dict[str, str] = {'name': 'Role Name', 'active': 'Active'}
    column_filters: tuple[str] = ('name', 'active')
    
class UserAdmin(AdminModelView):
    column_list: tuple[str] = ('username', 'name', 'surname', 'email', 'role_fk', 'active')
    column_labels: dict[str, str] = {'username': 'User Name','name': 'Name', 'surname': 'Surname', 'email': 'Email Address', 
                                     'role_fk': 'Role', 'active': 'Active'}
    column_filters: tuple[str] = ('username', 'name', 'surname', 'email', 'role_fk.name', 'active')
    