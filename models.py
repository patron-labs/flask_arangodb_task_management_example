from arango_orm import Collection, fields
from arango_orm.fields import String, Date,Integer,Field,DateTime,List,Boolean
from arango_orm import Graph, GraphConnection, Relation


class People(Collection):
    __collection__ = 'people'

    _key = String(required=True)
    name = String(required=True)

    def __str__(self):
        return "<Subject({})>".format(self.name)


class Categories(Collection):
    __collection__ = 'categories'
    _key = String(required=True)
    name = String(required=True)

    def __str__(self):
        return "<Subject({})>".format(self.name)


class Tasks(Collection):
    __collection__ = 'tasks'
    _key = String(required=True)
    title = String(required=True)
    description = String(required=True)
    due_date = Date(allow_none=True)

    def __str__(self):
        return "<Subject({})>".format(self.title)


class Category_Relation(Relation):
    __collection__ = 'category_relation'
    _key = String(required=True)


class Assignee_Relation(Relation):
    __collection__ = 'assignee_relation'
    _key = String(required=True)


class Task_Graph(Graph):
    __graph__ = 'graph'
    graph_connections = [

        GraphConnection(Tasks, Assignee_Relation, People),
        GraphConnection(Categories, Category_Relation, Tasks)
    ]

