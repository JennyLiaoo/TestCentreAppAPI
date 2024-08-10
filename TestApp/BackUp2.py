# imports all necessary libraries
import json
from flask import Flask, jsonify, request
from pymongo import MongoClient
import bson.objectid
from bson.json_util import dumps
from bson.objectid import ObjectId
from marshmallow import Schema, fields, ValidationError
from flask_cors import CORS, cross_origin


def handle_object_id(obj):
    if isinstance(obj, bson.ObjectId):
        return str(obj)
    return TypeError


# Schema listing all the necessary json fields that needs to be included when receiving data to create a test
class TestCreationRequestBodySchema(Schema):
    testName = fields.Str(required=True)
    courseCode = fields.Str(required=True)
    calculator = fields.Boolean(required=True)
    testLength = fields.Number(required=True)
    notes = fields.Str(required=True)
    students = fields.List(fields.Str, required=True)
    date = fields.Date(required=True)
    period = fields.Number(required=True)
    teacherName = fields.Str(required=True)


# Schema listing all the necessary json fields that needs to be included when updating the data for a test
class TestUpdateRequestBodySchema(Schema):
    _id = fields.Str(required=True)
    testName = fields.Str(required=True)
    courseCode = fields.Str(required=True)
    calculator = fields.Boolean(required=True)
    testLength = fields.Number(required=True)
    notes = fields.Str(required=True)
    students = fields.List(fields.Str, required=True)
    date = fields.Date(required=True)
    period = fields.Number(required=True)
    startTime = fields.List(fields.Str, required=True)
    teacherName = fields.Str(required=True)


class StudentCreationSchema(Schema):
    studentName = fields.Str(required=True)
    email = fields.Str(required=True)
    extraTime = fields.Number(required=True)


# Schema listing all the necessary json fields that needs to be included when updating only the start time
class TestUpdateTimeRequestBodySchema(Schema):
    _id = fields.Str(required=True)
    startTime = fields.Str(required=True)


class CourseCreationRequestBodySchema(Schema):
    courseName = fields.Str(required=True)
    students = fields.List(fields.Str, required=True)


# connecting to the MongoDB server using localhost
client = MongoClient("localhost", 27017)

db = client.testApp  # getting the database
collectionTests = db.tests  # getting the collection of tests
collectionStudents = db.users  # database instance of the
collectionCourses = db.courses  # database instance of the

app = Flask(__name__)
cors = CORS(app)


# method for adding a test into the database
@app.route("/test", methods=['POST'])
def add_test():
    # checks the schema to verify or validate that all the necessary fields are given in the json file
    json_data = request.get_json()
    try:
        result = TestCreationRequestBodySchema().load(json_data)
    except ValidationError as err:  # throws an error instead of causing the whole program to break
        return '', 400

    response = request.get_json()

    # adding the test into the collection
    collectionTests.insert_one({
        "testName": response["testName"],
        "courseCode": response["courseCode"],
        "calculator": response["calculator"],
        "testLength": response["testLength"],
        "notes": response["notes"],
        "students": response["students"],
        "date": response["date"],
        "period": response["period"],
        "startTime": None,
        "teacherName": response["teacherName"]
    })

    return '', 201


@app.route("/test", methods=['DELETE'])
def delete_test():
    response = request.get_json()
    id = response["_id"]

    collectionTests.delete_one({
        "_id": ObjectId(id)
    })

    return '', 200


@app.route("/test", methods=['PATCH'])
def update_test():
    response = request.get_json()
    try:
        result = TestUpdateRequestBodySchema().load(response)
    except ValidationError as err:
        return '', 400

    id = response["_id"]
    collectionTests.update_one({"_id": ObjectId(id)},  # where we find the thing with the given name, and we change
                               # the value's breed to the given value
                               {"$set": {"testName": response["testName"]}})
    collectionTests.update_one({"_id": ObjectId(id)},  # where we find the thing with the given name, and we change
                               # the value's breed to the given value
                               {"$set": {"courseCode": response["courseCode"]}})
    collectionTests.update_one({"_id": ObjectId(id)},  # where we find the thing with the given name, and we change
                               # the value's breed to the given value
                               {"$set": {"calculator": response["calculator"]}})
    collectionTests.update_one({"_id": ObjectId(id)},  # where we find the thing with the given name, and we change
                               # the value's breed to the given value
                               {"$set": {"testLength": response["testLength"]}})
    collectionTests.update_one({"_id": ObjectId(id)},  # where we find the thing with the given name, and we change
                               # the value's breed to the given value
                               {"$set": {"notes": response["notes"]}})
    collectionTests.update_one({"_id": ObjectId(id)},  # where we find the thing with the given name, and we change
                               # the value's breed to the given value
                               {"$set": {"students": response["students"]}})
    collectionTests.update_one({"_id": ObjectId(id)},  # where we find the thing with the given name, and we change
                               # the value's breed to the given value
                               {"$set": {"date": response["date"]}})
    collectionTests.update_one({"_id": ObjectId(id)},  # where we find the thing with the given name, and we change
                               # the value's breed to the given value
                               {"$set": {"period": response["period"]}})
    collectionTests.update_one({"_id": ObjectId(id)},  # where we find the thing with the given name, and we change
                               # the value's breed to the given value
                               {"$set": {"startTime": response["startTime"]}})
    collectionTests.update_one({"_id": ObjectId(id)},  # where we find the thing with the given name, and we change
                               # the value's breed to the given value
                               {"$set": {"teacherName": response["teacherName"]}})
    return '', 201


@app.route("/test/start", methods=['PATCH'])
def update_testStartTime():
    response = request.get_json()
    try:
        result = TestUpdateTimeRequestBodySchema().load(response)
    except ValidationError as err:
        return '', 400

    id = response["_id"]

    collectionTests.update_one({"_id": ObjectId(id)},  # where we find the thing with the given name, and we change
                               # the value's breed to the given value
                               {"$set": {"startTime": response["startTime"]}})
    return '', 201


# removing $oid and setting _id directly to the id string itself
def flatten_oid(obj):
    old_id = obj["_id"]
    obj["id"] = str(old_id)
    del obj["_id"]
    return obj


# gets the test based on the given filters.
@app.route("/test", methods=['GET'])
def get_test():
    testName = request.args.get('testName')
    courseCode = request.args.get('courseCode')
    date = request.args.get('date')
    period = request.args.get('period')

    query_filter = {}

    if testName is not None:
        query_filter["testName"] = testName
        # cursor = cursor.find({"testName": testName})
    if courseCode is not None:
        query_filter["courseCode"] = courseCode
        # cursor = cursor.find({"courseCode": courseCode})
    if period is not None:
        query_filter["period"] = period
        # cursor = cursor.find({"period": period})
    if date is not None:
        query_filter["date"] = date
        # cursor = cursor.find({"date": date})

    cursor = collectionTests.find(query_filter)

    data = []
    for doc in cursor:
        data.append(doc)

    json_data = []
    for doc in data:
        json_data.append(flatten_oid(doc))

    return json_data, 200  # dumps = puts all stuff into JSON


@app.route("/students", methods=['POST'])
def add_student():
    # for schema checks (validation):
    json_data = request.get_json()
    try:
        result = StudentCreationSchema().load(json_data)
    except ValidationError as err:
        return '', 400

    response = request.get_json()

    collectionStudents.insert_one({  # adding given users into a collection
        "name": response["name"],
        "email": response["email"],
        "extraTime": response["extraTime"],

    })
    return '', 201


# is fine
@app.route("/students", methods=['DELETE'])
def delete_student():
    response = request.get_json()
    id = response["_id"]

    collectionStudents.delete_one({
        "_id": ObjectId(id)
    })

    return '', 200


@app.route("/students", methods=['PATCH'])
def update_student():
    response = request.get_json()
    try:
        result = StudentCreationSchema().load(response)
    except ValidationError as err:
        return '', 400

    id = response["_id"]
    collectionStudents.update_one({"_id": ObjectId(id)},  # where we find the thing with the given name, and we change
                                  # the value's breed to the given value
                                  {"$set": {"name": response["name"]}})
    collectionStudents.update_one({"_id": ObjectId(id)},  # where we find the thing with the given name, and we change
                                  # the value's breed to the given value
                                  {"$set": {"email": response["email"]}})
    collectionStudents.update_one({"_id": ObjectId(id)},  # where we find the thing with the given name, and we change
                                  # the value's breed to the given value
                                  {"$set": {"extraTime": response["extraTime"]}})
    return '', 201


@app.route("/students", methods=['GET'])  # method used in insomnia
def get_student():
    name = request.args.get('name')
    email = request.args.get('email')
    extraTime = request.args.get('extraTime')

    query_filter = {}

    if name is not None:
        query_filter["name"] = name
    if email is not None:
        query_filter["email"] = email
    if extraTime is not None:
        query_filter["extraTime"] = extraTime

    cursor = collectionStudents.find(query_filter)

    data = []
    for doc in cursor:
        data.append(doc)

    json_data = []
    for doc in data:
        json_data.append(flatten_oid(doc))

    return json_data, 200  # dumps = puts all stuff into JSON


@app.route("/course", methods=['POST'])
def add_course():
    # for schema checks (validation):
    json_data = request.get_json()
    try:
        result = CourseCreationRequestBodySchema().load(json_data)
    except ValidationError as err:
        return '', 400
    response = request.get_json()

    student = response["students"]
    listOfStudents = []
    for x in student:
        listOfStudents.append(ObjectId(x))

    collectionCourses.insert_one({  # adding given users into a collection
        "courseName": response["courseName"],
        "students": listOfStudents
    })

    return '', 201


@app.route("/course", methods=['DELETE'])
def delete_course():
    response = request.get_json()
    id = response["_id"]

    collectionCourses.delete_one({
        "_id": ObjectId(id)
    })

    return '', 200


@app.route("/course", methods=['PATCH'])
def update_course():
    response = request.get_json()
    try:
        result = CourseCreationRequestBodySchema().load(response)
    except ValidationError as err:
        return '', 400

    student = response["students"]
    listOfStudents = []
    for x in student:
        listOfStudents.append(ObjectId(x))

    id = response["_id"]
    collectionCourses.update_one({"_id": ObjectId(id)},  # where we find the thing with the given name, and we change
                                 # the value's breed to the given value
                                 {"$set": {"courseName": response["courseName"]}})
    collectionCourses.update_one({"_id": ObjectId(id)},  # where we find the thing with the given name, and we change
                                 # the value's breed to the given value
                                 {"$set": {"students": listOfStudents}})

    return '', 201


# Gets the courses given the course, and returns the course name and the students who take the course
@app.route("/course", methods=['GET'])  # method used in insomnia
def get_course():
    # gets the name of the courses in the json file
    courseName = request.args.get('courseName')

    query_filter = {}

    if courseName is not None:
        query_filter["courseName"] = courseName

    cursor = collectionCourses.find(query_filter)

    data = []
    for doc in cursor:
        data.append(doc)

    json_data = []
    for doc in data:
        json_data.append(flatten_oid(doc))

    return json_data, 200  # dumps = puts all stuff into JSON


@app.route("/upload", methods=['POST'])
def upload():
    response = request.get_json()

    student_data = set((data["studentName"], data["email"]) for data in response) # Is like run add to the set again and again

    students = [{
        "name": data[0],
        "email": data[1],
        "extraTime": 0
    } for data in student_data]

    collectionStudents.insert_many(students)

    course_data = set(data["courseName"] for data in response) # Is like run add to the set again and again

    courses = [{
        "courseName": data,
        "students": [],
    } for data in course_data]

    collectionCourses.insert_many(courses)

    return "", 200  # dumps = puts all stuff into JSON


if __name__ == "__main__":
    app.run(debug=True, port=3000)