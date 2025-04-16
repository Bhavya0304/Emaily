from neo4j import GraphDatabase
from neo4j import Driver

def Connect(uri:str,username:str,password:str) -> Driver:
    return GraphDatabase.driver(uri,auth=(username,password))


