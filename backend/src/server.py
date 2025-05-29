from flask import Flask
import sys
from os import listdir
from os.path import isfile,join

app = Flask(__name__)

@app.route('/')
def Home():
    return 'Home'


@app.route('/<path:route>')
def controller(route):
    GetController(route)
    return 'Hello World'


def PreloadController():
    path = os.path.abspath(os.curdir)
    controllers = [f for f in listdir(join(path,"/src/api/")) if isfile(join(join(path,"/src/api/"), f))]
    print(controller)
    

def GetController(route):
    controller = route.split('/')[0]
    action = route.split('/')[1] if len(route.split('/')) > 1 else ''
    remaining = '/'.join(route.split('/')[1:]) if len(route.split('/')) > 2 else ''
    print(controller)
    print(action)
    print(remaining)