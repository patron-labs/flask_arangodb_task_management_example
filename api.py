import json
from datetime import datetime, date
from flask import request, jsonify

from models import Tasks, People, Categories, Category_Relation, Assignee_Relation
from __init__ import flask_app,db,task_graph


# lists all the people
@flask_app.route('/people/list',methods=['GET'])
def list_people():
    people = db.query(People).all()
    result = []
    for person in people:
        result.append(person._dump())

    return jsonify({'result':result})


# adds a new record to people collection
@flask_app.route('/people/add', methods=['POST'])
def add_new_person():
    body = json.loads(request.data)
    name = body.get('name',None)
    if name is None:
        return jsonify({'error':'name cannot be null'})
    new_person = People(name=name)
    db.add(new_person)
    return jsonify({'result':new_person._dump()})


# edits record in people collection
@flask_app.route('/people/edit',methods=['PUT'])
def edit_person():
    body = json.loads(request.data)
    key = body.get('_key',None)
    if key is None:
        return jsonify({'error':'key cannot be null'})

    name = body.get('name',None)
    if name is None:
        return jsonify({'error':'name cannot be null'})

    person = db.query(People).by_key(key)
    person.name = name
    db.update(person)

    return jsonify({'result':person._dump()})


# deletes a record in people collection
@flask_app.route('/people/remove', methods=['DELETE'])
def delete_person():
    body = json.loads(request.data)
    key = body.get('_key', None)
    if key is None:
        return jsonify({'error': 'key cannot be null'})

    person = db.query(People).by_key(key)
    db.delete(person)
    return jsonify({'result': 'success'})


# lists all the tasks
@flask_app.route('/task/list', methods=['GET'])
def list_tasks():
    tasks = db.query(Tasks).all()
    result = []
    for task in tasks:
        task_dict = task._dump()
        task_graph.expand(task, depth=1, direction='any')
        assignee_name = task._relations['assignee_relation'][0]._object_to.name
        category_name = task._relations['category_relation'][0]._object_from.name
        task_dict['assignee'] = assignee_name
        task_dict['category'] = category_name

        result.append(task_dict)

    return jsonify({'result': result})


# add new task
@flask_app.route('/task/add',methods=['POST'])
def add_new_task():
    body = json.loads(request.data)
    title = body.get('title', None)
    description = body.get('description', None)

    due_date = body.get('due_date', None)
    if due_date is not None:
        due_date = datetime.strptime(due_date , '%Y-%m-%d').date()

    new_task = Tasks(title=title, description=description, due_date=due_date)

    db.add(new_task)

    # Add assignee relation
    assignee_key = body.get('assignee_key',None)
    assignee = db.query(People).by_key(assignee_key)
    if assignee_key is not None:
        db.add(task_graph.relation(new_task, Assignee_Relation(), assignee))

    # Add category relation
    category_key = body.get('category_key', None)
    category = db.query(Categories).by_key(category_key)

    if category is not None:
        db.add(task_graph.relation(relation_from=category, relation=Category_Relation(), relation_to=new_task))

    return jsonify({'result': new_task._dump()})


# edit task
@flask_app.route('/task/edit', methods=['PUT'])
def edit_task():
    body = json.loads(request.data)
    task_key = body.get('_key', None)
    task = db.query(Tasks).by_key(task_key)
    if task is None:
        return jsonify({'message':'task not found'})

    name = body.get('name',None)
    description = body.get('description', None)
    task.name = name
    task.description = description
    db.update(task)

    category_key = body.get('category_key', None)
    category = db.query(Categories).by_key(category_key)
    if category is not None:
        # find old category relation and delete it
        old_category_relation = db.query(Category_Relation).filter('_to==@_to',_to=task._id).first()
        db.delete(old_category_relation)

        # add new category relation
        db.add(task_graph.relation(relation_from=category, relation=Category_Relation(), relation_to=task))

    assignee_key = body.get('assignee_key', None)
    assignee = db.query(People).by_key(assignee_key)
    if assignee is not None:
        # find old assignee relation and delete it
        old_assignee_relation = db.query(Assignee_Relation).filter('_from==@_from',_from=task._id).first()
        db.delete(old_assignee_relation)

        # add new assignee relation
        db.add(task_graph.relation(relation_from=task, relation=Assignee_Relation(), relation_to=assignee))

    return jsonify({'result':task._dump()}), 200


# delete task
@flask_app.route('/task/remove', methods=['DELETE'])
def remove_task():
    body = json.loads(request.data)
    task_key = body.get('_key', None)
    task = db.query(Tasks).by_key(task_key)
    if task is None:
        return jsonify({'message': 'task not found'})

    db.delete(task)
    return jsonify(({'message':'success'}))


# lists all the categories
@flask_app.route('/categories/list', methods=['GET'])
def get_categories():
    categories = db.query(Categories).all()
    result = []
    for cat in categories:
        result.append(cat._dump())

    return jsonify({'result': result}), 200


# add new category
@flask_app.route('/categories/add', methods=['POST'])
def add_categories():
    body = json.loads(request.data)
    category_name = body.get('name', None)
    category = Categories(name=category_name)
    db.add(category)
    return jsonify({'result': category._dump()}) , 200


# edit category
@flask_app.route('/categories/edit', methods=['PUT'])
def edit_categories():
    body = json.loads(request.data)
    category_name = body.get('name', None)
    category_key = body.get('_key',None)
    category = db.query(Categories).by_key(category_key)
    if category is not None:
        category.name = category_name
        db.update(category)
    else:
        return jsonify({'error':'Category not found'}), 200

    return jsonify({'result': category._dump()}), 200


# delete category
@flask_app.route('/categories/remove', methods=['DELETE'])
def remove_categories():
    body = json.loads(request.data)
    category_key = body.get('_key', None)
    category = db.query(Categories).by_key(category_key)
    if category is not None:
        db.delete(category)
    else:
        return jsonify({'error':'Category not found'}), 200
    return jsonify({'result': 'success'}), 200
