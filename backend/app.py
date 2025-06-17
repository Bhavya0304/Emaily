import sys

sys.dont_write_bytecode = True


from flask import Flask,request,Response
from flask_cors import CORS
import sys
import os
from os import listdir
from os.path import isfile,join
from helper import load_env
from helper.logger import SingletonLogger,LogTypes
app = Flask(__name__)

def custom_cors_origin(origin):
    return origin.endswith(".joshibhavya.com") or origin == "https://joshibhavya.com"

CORS(app,origins=custom_cors_origin)

load_env.Load()
# instantiate Default Logger 
SingletonLogger()

@app.route('/')
def Home():
    return "Hello World"


@app.route('/<path:route>',methods = ['POST','GET'])
def controller(route):
    try:
        return GetController(route)
    except Exception as ex:
        print("Global Error")
        SingletonLogger().get_logger().Log(LogTypes.Global,str(ex))
        return Response("Something Went Wrong",status=500)

def PreloadController():
    path = os.path.abspath(os.curdir)
    api_path = os.path.join(path, "src", "api")
    controllers = [f for f in listdir(api_path) if isfile(join(api_path, f))]
    controllers.remove("__init__.py")
    controllerObj = []
    for controller in controllers:
        module_name = "src.api." + controller.replace(".py","")
        __import__(module_name)
        mod = sys.modules[module_name]
        cls_name = controller.replace(".py", "")
        controller_class = getattr(mod, cls_name)
        controllerObj.append(controller_class)
    return controllerObj


def GetController(route):
    controller = route.split('/')[0]
    action = route.split('/')[1] if len(route.split('/')) > 1 else ''
    remaining = '/'.join(route.split('/')[1:]) if len(route.split('/')) > 2 else ''
    controllers = PreloadController()
    for ctrl_class in controllers:
        if ctrl_class.__name__.lower() == controller.lower() + "controller":
            instance = ctrl_class()  # instantiate the controller class
            
            if hasattr(instance, action):
                method = getattr(instance, action)
                return method(request)  # pass the remaining path as arg (optional)
            else:
                return Response("Action Not Found",status=400)
    
    return Response("Controller Not Found",status=400)



