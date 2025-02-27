#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# Copyright 2021 Graeme Keates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask


import flask
from flask import Flask, redirect, request
import json
app = Flask(__name__)
app.debug = True

# An example world
# {
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }

class World:
    def __init__(self):
        self.clear()

    def update(self, entity, key, value):
        entry = self.space.get(entity, dict())
        entry[key] = value
        self.space[entity] = entry

    def set(self, entity, data):
        self.space[entity] = data

        # Notify all listeners
        for l in self.listeners.keys():
            self.listeners[l][entity] = data

    def set_world(self, data):
        self.space = data

    def clear(self):
        self.space = dict()
        self.listeners = dict()

    def add_listener(self, id):
        self.listeners[id] = dict()

    def get_bucket(self, id):
        return self.listeners[id]

    def clear_bucket(self, id):
        self.listeners[id] = dict()

    def get(self, entity):
        return self.space.get(entity,dict())

    def world(self):
        return self.space

# you can test your webservice from the commandline
# curl -v   -H "Content-Type: application/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}'

myWorld = World()

# I give this to you, this is how you get the raw body/data portion of a post in flask
# this should come with flask but whatever, it's not my project.
def flask_post_json():
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data.decode("utf8") != u''):
        return json.loads(request.data.decode("utf8"))
    else:
        return json.loads(request.form.keys()[0])

@app.route("/")
def hello():
    '''Return something coherent here.. perhaps redirect to /static/index.html '''
    return redirect('/static/index.html', code=302)

@app.route("/entity/<entity>", methods=['POST','PUT'])
def update(entity):
    '''update the entities via this interface'''
    input_json = flask_post_json()
    if 'body' in input_json.keys():
        data = input_json['body']
    else:
        data = input_json

    if request.method == 'PUT':
        # Set
        myWorld.set(entity, data)

    elif request.method == 'POST':
        # Update
        for key, value in data.items():
            myWorld.update(entity, key, value)

    e = myWorld.get(entity)
    return flask.jsonify(e)

@app.route("/world", methods=['POST','GET'])
def world():
    '''you should probably return the world here'''
    if request.method == 'POST':
        data = flask_post_json()
        myWorld.set_world(data)

    return myWorld.world()

@app.route("/entity/<entity>")
def get_entity(entity):
    '''This is the GET version of the entity interface, return a representation of the entity'''
    e = myWorld.get(entity)
    return flask.jsonify(e)


@app.route("/listener/<id>", methods=['POST','PUT'])
def add_listener(id):
    '''Add a listener'''
    myWorld.add_listener(id)
    return flask.jsonify(id)

@app.route("/listener/<id>")
def get_bucket(id):
    '''GET listener bucket, return entities that have yet to be sent'''
    data = myWorld.get_bucket(id)
    myWorld.clear_bucket(id)
    return flask.jsonify(data)

@app.route("/clear", methods=['POST','GET'])
def clear():
    '''Clear the world out!'''
    myWorld.clear()
    return myWorld.world()

if __name__ == "__main__":
    app.run()
