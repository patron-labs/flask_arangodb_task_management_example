from flask import Flask
from arango import ArangoClient
from arango_orm import Database
from models import Task_Graph, People, Categories, Tasks

app = Flask(__name__)


client = ArangoClient(hosts='http://127.0.0.1:8529')

# Retrieve _system database from arangodb (_system database is default)
sys_db = client.db('_system', username='root', password='openSesame')

# Check if task database exist, create one if doesnt exist
if not sys_db.has_database('task_db'):
    sys_db.create_database('task_db')

# Initialize task db
task_db_client = client.db('task_db', username='root', password='openSesame')
db = Database(task_db_client)
task_graph = Task_Graph(connection=db)

db.create_all([Task_Graph, People, Categories, Tasks])
