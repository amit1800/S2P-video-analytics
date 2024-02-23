from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
from base.models import CUser
from base import views as base_view
from asgiref.sync import sync_to_async
# Create your views here.


@api_view(["POST"])
def authenticate(request):
    us = request.data["username"]
    pw = request.data["password"]
    # print(us, make_password(pw))
    if base_view.isAuthenticated(us, pw): 
        return Response({"auth": True})
    else:
        return Response({"auth": False})
    
@api_view(["POST"])
def adduser(request):
    try:
        username = request.data["username"]
        password = request.data["password"]
        firstname = request.data["firstname"]
        lastname = request.data["lastname"]
        res = base_view.createNewUser(firstname, lastname,username, password)
        #perform user creation query
        return res
    except:
        return Response({"status": False})

@api_view(["POST"])
def getStreamNames(request):
    username = request.data["username"]
    res = base_view.getAcitveTracksForUser(username)
    return res