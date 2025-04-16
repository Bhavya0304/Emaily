from neo4j import Driver
import uuid
from typing import Optional, List


class Objects:
    def __init__(self):
        if not hasattr(self, 'id'):
            self.id = str(uuid.uuid4())

    def __str__(self):
        keys = list(vars(self).keys())
        obj_str = str(vars(self))
        for key in keys:
            if vars(self)[key] == None:
                obj_str = obj_str.replace(f", '{key}': {vars(self)[key]}","")
                obj_str = obj_str.replace(f"'{key}': {vars(self)[key]},","")
                obj_str = obj_str.replace(f"'{key}': {vars(self)[key]}","")
            else:
                obj_str = obj_str.replace(f"'{key}':",f"{key}:")
        return obj_str

def Type(type):
    def Wrapper(cls):
        cls._obj_type = type
        return cls
    return Wrapper



class Query:
    def __init__(self, driver: Driver, db: str):
        self.Driver: Driver = driver
        self.db = db

    def UpsertNode(self, node: Objects):
        if getattr(node, '_obj_type', None) == "Node":
            props = str(node)
            query = f"MERGE (n:{node.__class__.__name__} {props})"
            summary = self.Driver.execute_query(query, database_=self.db)
            print(summary)
        else:
            raise Exception("Object type is not 'Node'")

    def DeleteNode(self, node: Objects):
        if getattr(node, '_obj_type', None) == "Node":
            props = str(node)
            query = f"MATCH (n:{node.__class__.__name__} {props}) DETACH DELETE n"
            self.Driver.execute_query(query, database_=self.db)
        else:
            raise Exception("Object type is not 'Node'")

    def AssociateNode(self, nodeFrom: Objects, nodeTo: Objects, relationship: Objects):
        if all(getattr(n, '_obj_type', None) == "Node" for n in [nodeFrom, nodeTo]) and getattr(relationship, '_obj_type', None) == "Relationship":
            propsFrom = str(nodeFrom)
            propsTo = str(nodeTo)
            relProps = str(relationship)
            relType = relationship.__class__.__name__.upper()

            query = (
                f"MATCH (a:{nodeFrom.__class__.__name__} {propsFrom}), "
                f"(b:{nodeTo.__class__.__name__} {propsTo}) "
                f"MERGE (a)-[r:{relType} {relProps}]->(b)"
            )
            self.Driver.execute_query(query, database_=self.db)
        else:
            raise Exception("Invalid types for nodes or relationship")

    def DeassociateNode(self, nodeFrom: Objects, nodeTo: Objects, relationship: Objects):
        if all(getattr(n, '_obj_type', None) == "Node" for n in [nodeFrom, nodeTo]) and getattr(relationship, '_obj_type', None) == "Relationship":
            propsFrom = str(nodeFrom)
            propsTo = str(nodeTo)
            relProps = str(relationship)
            relType = relationship.__class__.__name__.upper()

            query = (
                f"MATCH (a:{nodeFrom.__class__.__name__} {propsFrom})-"
                f"[r:{relType} {relProps}]->"
                f"(b:{nodeTo.__class__.__name__} {propsTo}) "
                f"DELETE r"
            )
            self.Driver.execute_query(query, database_=self.db)
        else:
            raise Exception("Invalid types for nodes or relationship")

    def GetNode(self, node: Objects):
        if getattr(node, '_obj_type', None) == "Node":
            props = str(node)
            query = f"MATCH (n:{node.__class__.__name__} {props}) RETURN n"
            result = self.Driver.execute_query(query, database_=self.db)
            return result
        else:
            raise Exception("Object type is not 'Node'")

    def GetNodesByLabel(self, label: str):
        query = f"MATCH (n:{label}) RETURN n"
        result = self.Driver.execute_query(query, database_=self.db)
        return result

    def GetRelatedNodes(self, node: Objects, relType: str, direction: str = "OUTGOING", depth: int = 1):
        if getattr(node, '_obj_type', None) != "Node":
            raise Exception("Object type is not 'Node'")

        props = str(node)
        label = node.__class__.__name__
        depth_clause = f"*1..{depth}" if depth > 1 else ""

        if direction == "OUTGOING":
            query = (
                f"MATCH (n:{label} {props})-[:{relType}{depth_clause}]->(related) "
                f"RETURN DISTINCT related"
            )
        elif direction == "INCOMING":
            query = (
                f"MATCH (n:{label} {props})<-[:{relType}{depth_clause}]-(related) "
                f"RETURN DISTINCT related"
            )
        else:
            query = (
                f"MATCH (n:{label} {props})-[:{relType}{depth_clause}]-(related) "
                f"RETURN DISTINCT related"
            )

        result = self.Driver.execute_query(query, database_=self.db)
        return result

    def GetRelationshipsBetween(self, nodeFrom: Objects, nodeTo: Objects, relType: Optional[str] = None):
        if any(getattr(n, '_obj_type', None) != "Node" for n in [nodeFrom, nodeTo]):
            raise Exception("Both objects must be of type 'Node'")

        propsFrom = str(nodeFrom)
        propsTo = str(nodeTo)
        labelFrom = nodeFrom.__class__.__name__
        labelTo = nodeTo.__class__.__name__

        rel = f":{relType}" if relType else ""
        query = (
            f"MATCH (a:{labelFrom} {propsFrom})-[r{rel}]-(b:{labelTo} {propsTo}) "
            f"RETURN r"
        )
        result = self.Driver.execute_query(query, database_=self.db)
        return result

    def GetNodeCount(self, label: Optional[str] = None):
        if label:
            query = f"MATCH (n:{label}) RETURN count(n) as count"
        else:
            query = f"MATCH (n) RETURN count(n) as count"

        result = self.Driver.execute_query(query, database_=self.db)
        return result

    def GetAll(self, limit: int = 100):
        query = f"MATCH (n) RETURN n LIMIT {limit}"
        result = self.Driver.execute_query(query, database_=self.db)
        return result

    def GetByCypher(self, query: str):
        if not query.strip().lower().startswith("match"):
            raise Exception("Only read queries are allowed in GetByCypher")

        result = self.Driver.execute_query(query, database_=self.db)
        return result