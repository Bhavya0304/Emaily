import sys
from flask import Response,json,Request
from ..helper import auth
import os
from db.neograph.core import Connect
from db.neograph.engine.query import Query
from ..models.category import Category,UserCategories
from ..models.user import User

class categoryController:
    def __init__(self):
        pass

    def get_query(self):
        driver = Connect.Connect(
            os.getenv("NEO4J_URL"),
            os.getenv("NEO4J_USER"),
            os.getenv("NEO4J_PASSWORD")
        )
        return Query(driver, "emailydb")

    @auth.Authuenticate
    def get(self, req:Request):
        try:
            print(self.payload)
            user_id = self.payload.get("id")
            user = User()
            user.id = user_id

            query = self.get_query()
            categories = query.GetRelatedNodes(user, "USERCATEGORIES", direction="OUTGOING")

            cat_data = []
            for record in categories[0]:
                cat_node = record.data()["related"]
                cat_data.append(cat_node)

            return Response(json.dumps({"status": "success", "categories": cat_data}),200,mimetype="application/json")

        except Exception as e:
            return Response(json.dumps({"status": "error", "message": str(e)}), 500,mimetype="application/json")

    @auth.Authuenticate
    def create(self, req:Request):
        try:
            print(self.payload)
            data = req.get_json()
            user_id = self.payload.get("id")

            category = Category(
                name=data.get("name"),
                description=data.get("description"),
                precision=data.get("precision")
            )

            user = User()
            user.id = user_id

            query = self.get_query()
            query.UpsertNode(category)

            rel = UserCategories()
            categoryToAsso = Category()
            categoryToAsso.id = category.id

            query.AssociateNode(user, categoryToAsso, relationship=rel)

            return Response(json.dumps({"status": "created", "category": category.__dict__}), 201,mimetype="application/json")

        except Exception as e:
            return Response(json.dumps({"status": "error", "message": str(e)}), 500,mimetype="application/json")

    @auth.Authuenticate
    def update(self, req:Request):
        try:
            print(self.payload)
            data = req.get_json()
            category_id = data.get("id")  # Assuming category ID is passed in payload

            category = Category(
                name=data.get("name"),
                description=data.get("description"),
                precision=data.get("precision")
            )
            category.id = category_id

            query = self.get_query()
            query.UpsertNode(category)

            return Response(json.dumps({"status": "updated", "category": category.__dict__}),200,mimetype="application/json")

        except Exception as e:
            return Response(json.dumps({"status": "error", "message": str(e)}), 500,mimetype="application/json")

    @auth.Authuenticate
    def delete(self, req:Request):
        try:
            print(self.payload)
            data = req.get_json()
            category_id = data.get("id")  # Category ID to delete
            user_id = self.payload.get("id")

            category = Category()
            category.id = category_id

            user = User()
            user.id = user_id

            query = self.get_query()
            rel = UserCategories()
            query.DeassociateNode(user, category, rel)
            query.DeleteNode(category)

            return Response(json.dumps({"status": "deleted", "category_id": category_id}),200,mimetype="application/json")

        except Exception as e:
            return Response(json.dumps({"status": "error", "message": str(e)}), 500,mimetype="application/json")
        