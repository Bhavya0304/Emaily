# from db.neograph.engine.query import Query
# from db.neograph.core import Connect
# from db.schema import EmailAccount,Account,User

# user = User("Bhavya Joshi","bhavyajsh","123456","salt")
# user1 = User("Bhavya Joshi","bhavyajsh","123456")
# account = Account("12","Google","123","123","expiry","id",True)
# rel = EmailAccount()

# driver = Connect.Connect("neo4j://localhost","neo4j","D@rw1nPr0ject")
# q = Query(driver,"emailydb")
# q.UpsertNode(user)
# q.UpsertNode(account)
# q.AssociateNode(user,account,rel)

from flask import Flask,request
import sys
import os
from os import listdir
from os.path import isfile,join

app = Flask(__name__)

@app.route('/')
def Home():
    return 'Home'


@app.route('/<path:route>',methods = ['POST','GET'])
def controller(route):
    return GetController(route)


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
                return f"⚠️ Action '{action}' not found in controller '{controller}'"
    
    return f"❌ Controller '{controller}' not found"
