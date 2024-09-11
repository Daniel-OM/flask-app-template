
import os
import enum
import json
import datetime as dt

import numpy as np
import pandas as pd

from http import HTTPStatus
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, flash, redirect, render_template, request, url_for, Response, send_from_directory
from flask_login import login_required, current_user
from .config import config, serializer, config_email
from .models import db
from .api import (ApiResponse, MasterAPI, UserAPI, GoalAPI, UserGoalAPI, ConnectionAPI, AssetAPI)


user_api: UserAPI = UserAPI(db=db)

# Initialice the users module
user_views = Blueprint(name='user_views', import_name=__name__)

@user_views.route(rule='/register', methods=['GET', 'POST'])
def register() -> str | dict[str, (bool | str)]:
    errors: list[str] = []
    if request.method == 'POST':

        response: ApiResponse = user_api.checkByUser(username=request.form['username'], email=request.form['email'])
        if response.executed:
            exists: dict[str, bool] = response.data
            if any(exists.values()):
                
                if exists['username']:
                    errors.append('ERROR: The username is already in use, please try another one.')
                if exists['email']:
                    errors.append('ERROR: The email is already in use, please try another one.')

                return render_template(template_name_or_list='/user/register.html', navbar=False, footer=False, 
                                        errors=errors)
        else:
            errors.append(f'ERROR: {response.description}')

        # that user if so and it's accounts.
        response: ApiResponse = user_api.post(
            username=request.form['username'],
            email=request.form['email'],
            password=request.form['password'],
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            role_id=2,
            active=True
        )
        
        if response.executed:
            return redirect(location=url_for(endpoint='user_views.email_verification'))
        else:
            errors.append(f'ERROR: {response.description}')
            print('Error: ', response.description)
    
    return render_template(template_name_or_list='/user/register.html', navbar=False, footer=False, 
                           errors=errors)

@user_views.route(rule='/login', methods=['GET', 'POST'])
def login() -> Response | str | dict[str, (bool | str)]:
    errors: list[str] = []
    if request.method == 'POST':
        if user_api.isVerified(email=request.form['email']):
            response: ApiResponse = user_api.login(email=request.form['email'], password=request.form['password'])
            if response.executed:
                return redirect(location=url_for(endpoint='loged_views.dashboard'))
            elif response.status == ApiResponse.Status.SUCCESS:
                errors.append('ERROR: Check if the email and the password where correct.')
        else:
            return redirect(location=url_for(endpoint='user_views.email_verification'))
        
    return render_template(template_name_or_list='/user/login.html', navbar=False, footer=False, errors=errors)

@user_views.route(rule='/logout', methods=['GET', 'POST'])
@login_required
def logout() -> Response | dict[str, (bool | str)]:

    response: ApiResponse = user_api.logout()

    if response.executed:
        return redirect(location=url_for(endpoint='user_views.login'))
    else:
        return redirect(location=url_for(endpoint='loged_views.dashboard'))

@user_views.route(rule='/forgot-password', methods=['GET', 'POST'])
def forgot_password() -> dict[str, (bool | str)]:

    if request.method == 'POST':

        response: ApiResponse = user_api.forgotPassword(email=request.form['email'])

        if response.executed:
            flash(message=response.description, category='success')
            return redirect(location=url_for(endpoint='user_views.login'))
        elif response.status == ApiResponse.Status.SUCCESS:
            return render_template(template_name_or_list='/user/forgot_password.html', navbar=False, footer=False)
    
    return render_template(template_name_or_list='/user/forgot_password.html', navbar=False, footer=False)

@user_views.route(rule='/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token=None) -> Response | str:

    if request.method == 'POST':
        if request.form['password'] == request.form['repeat_password']:
            response: ApiResponse = user_api.userResetPassword(token=token, 
                                password=request.form['password'] if request.method == 'POST' else None)
            
            if response.executed:
                if current_user.is_authenticated:
                    return redirect(location=url_for(endpoint='loged_views.dashboard'))
                else:
                    flash(message=response.description, category='success')
                    return redirect(location=url_for(endpoint='user_views.login'))
            else:
                return render_template(template_name_or_list='/user/reset_password.html', token=token, modal=response.description)
            
    return render_template(template_name_or_list='/user/reset_password.html', token=token)

@user_views.route(rule="/detail", methods=['GET'])
@login_required
def user_detail() -> str:

    response: ApiResponse = user_api.getById(unwanted_keys=['_sa_instance_state', 'active', 'role_id'])
    
    return response.to_dict()

@user_views.route(rule="/edit", methods=["GET", "POST"])
@login_required
def user_edit() -> Response:
    
    data: dict = user_api.formToDict(form=request.form)
    
    if 'pricing' in data:
        response: ApiResponse = user_api.updateSubscription(subscription=data.get('subscription'), pricing=data['pricing'])
    response: ApiResponse = user_api.update(form={k: v for k, v in data.items() if k not in ['subscription', 'pricing']})
    
    response: ApiResponse = user_api.getById(unwanted_keys=['_sa_instance_state', 'active', 'role_id'])
    
    return redirect(location=url_for(endpoint='main_views.dashboard'))

@user_views.route(rule="/delete", methods=["GET", "POST"])
@login_required
def user_delete(forever:bool=False) -> dict:
    
    response: ApiResponse = user_api.delete(forever=forever)
    
    return response.to_dict()


# Initialice the page
main_views = Blueprint(name='main_views', import_name=__name__)

@main_views.route(rule="/<path:filename>")
def templates(filename) -> str:
    print(send_from_directory(directory='templates', path=filename))
    return send_from_directory(directory='templates', path=filename)

@main_views.route(rule="/", methods=['GET'])
def home() -> dict[str, (str | bool)]:
    return render_template(template_name_or_list='/home.html', navbar=True, footer=True)
