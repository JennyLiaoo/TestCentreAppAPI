####################  Setting Up  #######################
# importing libraries
from flask import Flask, request, redirect, json, make_response
from pymongo import MongoClient
import bson.objectid
from bson.objectid import ObjectId
from marshmallow import Schema, fields, ValidationError
from flask_cors import CORS
from os import environ
from dotenv import load_dotenv
from uuid import uuid4
import requests

load_dotenv()

# Setting up for OAuth (authentication)
mongodb_host = environ.get("MONGODB_HOST") or "localhost"
mongodb_port = 27017
mongodb_username = environ.get("MONGODB_USERNAME")
mongodb_password = environ.get("MONGODB_PASSWORD")

# initializing the connection to the MongoDB database and setting up a Flask application with CORS enabled
client = MongoClient(mongodb_host, mongodb_port, username=mongodb_username, password=mongodb_password)

# getting the database and its collections
db = client.testApp
collectionTests = db.tests
collectionStudents = db.users
collectionCourses = db.courses
collectionOAuthStates = db.oauthStates
collectionSessions = db.sessions

app = Flask(__name__)  # Initialize the Flask application
cors = CORS(app)  # Enable CORS for the Flask app


####################  Helper Methods  #######################

def handle_object_id(obj):
    """This method converts the obj into a string if the given obj is an instance of bson.ObjectId

    :param obj: The object to be converted
    :return: The string representation of the object if it is an instance of bson.ObjectId
    :raise: TypeError if the obj is not an instance of bson.ObjectId.
    """
    if isinstance(obj, bson.ObjectId):
        return str(obj)
    return TypeError


def flatten_oid(obj):
    """This method removes the embedded $oid field, making it easier for the frontend to handle.

    :param obj: A dictionary containing an "_id" field to be flattened.
    :return: The new _id without embedded $oid
    """
    old_id = obj["_id"]
    obj["id"] = str(old_id)
    del obj["_id"]
    return obj


####################  Schemas  #######################

class TestCreationRequestBodySchema(Schema):
    """Schema for validating the request body when creating a new test.

    :param testName: The name of the test. Required.
    :param courseCode: The course code for which the test is being created. Required.
    :param calculator: Whether a calculator is permitted for the test. Required, should be a boolean value.
    :param testLength: The length of the test in minutes. Required, should be a number.
    :param notes: Any additional notes or instructions for the test. Required.
    :param students: A list of student IDs for whom the test is intended. Required, each ID should be a string.
    :param date: The date of the test. Required, should be a date format.
    :param period: The period or session for the test. Required, should be a number.
    :param teacherName: The name of the teacher creating the test. Required.
    """
    testName = fields.Str(required=True)
    courseCode = fields.Str(required=True)
    calculator = fields.Boolean(required=True)
    testLength = fields.Number(required=True)
    notes = fields.Str(required=True)
    students = fields.List(fields.Str, required=True)
    date = fields.Date(required=True)
    period = fields.Number(required=True)
    teacherName = fields.Str(required=True)


class TestUpdateRequestBodySchema(Schema):
    """Schema for validating the request body when updating a test.

    :param _id: The ID of the test to be updated. Required.
    :param testName: The updated name of the test. Required.
    :param courseCode: The updated course code for which the test is being created. Required.
    :param calculator: Whether a calculator is allowed for the test. Required, should be a boolean value.
    :param testLength: The updated length of the test in minutes. Required, should be a number.
    :param notes: Any additional notes or instructions for the test. Required.
    :param students: A list of student IDs for whom the test is intended. Required, each ID should be a string.
    :param date: The updated date of the test. Required, should be a date format.
    :param period: The updated period or session for the test. Required, should be a number.
    :param startTime: The updated start times of the test. Required, should be a list of strings.
    :param teacherName: The updated name of the teacher creating the test. Required.
    """
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
    """Schema for validating the request body when creating a new student.

    :param studentName: The name of the student. Required.
    :param email: The email address of the student. Required.
    :param extraTime: The amount of extra time (min) the student is allowed for tests. Required, should be a number.
    """
    studentName = fields.Str(required=True)
    email = fields.Str(required=True)
    extraTime = fields.Number(required=True)


class StudentExtraTimeRequestBodySchema(Schema):
    """Schema for validating the request body when updating a student's extra time for a test.

    :param studentName: The name of the student for which extra time needs to be added to. Required.
    :param extraTime: The updated extra time needed for the test. Required, should be a Number.
    """
    studentName = fields.Str(required=True)
    extraTime = fields.Number(required=True)


class StudentExtraTimeRequestBodySchemaArray(Schema):
    """Schema for validating the request body when updating a student's extra time for a test when given a json with a list of students.

    :param arrayStudents: The array of students who need to have extra time added to them. Required.
    """
    arrayStudents = fields.List(fields.Nested(StudentExtraTimeRequestBodySchema), required=True)


class TestUpdateTimeRequestBodySchema(Schema):
    """Schema for validating the request body when updating the start time of a test.

    :param _id: The ID of the test for which the start time is being updated. Required.
    :param startTime: The updated start time of the test. Required, should be a string in HH:MM format.
    """
    _id = fields.Str(required=True)
    startTime = fields.List(fields.Str, required=True)


class CourseCreationRequestBodySchema(Schema):
    """Schema for validating the request body when creating a new course.

    :param courseName: The name of the course. Required.
    :param students: A list of student IDs enrolled in the course. Required, each ID should be a string.
    """
    courseName = fields.Str(required=True)
    students = fields.List(fields.Str, required=True)


class initialUploadRequestBodySchema(Schema):
    """Schema for validating the request body when uploading the data from the CSV file to the database

    :param studentName: The name of the student. Required.
    :param email: The student's email. Required
    :param courseName: The name of the courses. Required
    """
    studentName = fields.Str(required=True)
    email = fields.Str(required=True)
    courseName = fields.Str(required=True)


class initialUploadRequestBodySchemaArray(Schema):
    """Schema for validating the request body when uploading the data from the CSV file to the database as an array.

    :param arrayStudents: The array of students who need to be uploaded. Required.
    """
    arrayStudents = fields.List(fields.Nested(initialUploadRequestBodySchema), required=True)


####################  Bulk uploading data  #######################

@app.route("/upload", methods=['POST'])
def upload():
    """
    Uploads student and course data to the 'students' and 'courses' collections in the 'testApp' database.

    Returns:
    - 201 Created: If the data is successfully uploaded to the collections.
    - 400 Bad Request: If the JSON payload does not contain all the necessary fields or has invalid data types.
    """

    # checks the schema to verify or validate that all the necessary fields are given in the json file
    json_data = request.get_json()
    try:
        result = initialUploadRequestBodySchemaArray().load(json_data)
    except ValidationError as err:  # throws an error instead of causing the whole program to break
        return '', 400  # bad request

    response = json_data["arrayStudents"]

    # completely clears the database
    collectionStudents.delete_many({})
    collectionTests.delete_many({})
    collectionCourses.delete_many({})

    # using a set, add all the students from the given file and upload them into the database using a for loop
    student_data = set(
        (data["studentName"], data["email"]) for data in response)

    students = [{
        "name": data[0],
        "email": data[1],
        "extraTime": 0
    } for data in student_data]

    collectionStudents.insert_many(students)  # inserts all the students into the student collection

    # Does the same thing for uploading all the courses in the given file
    course_data = set(data["courseName"] for data in response)
    courses = [{
        "courseName": data,
        "students": [],
    } for data in course_data]

    collectionCourses.insert_many(courses)

    return "", 201  # Created


####################  Managing the test database  #######################

@app.route("/test", methods=['POST'])
def add_test():
    """Adds a new test to the 'tests' collection in the 'testApp' database.

    This route expects a JSON with the following fields according to the TestCreation Schema
    - testName (str): The name of the test.
    - courseCode (str): The course code for which the test is being created.
    - calculator (bool): Whether a calculator is allowed for the test.
    - testLength (int): The length of the test in minutes.
    - notes (str): Any additional notes or instructions for the test.
    - students (list of str): A list of student IDs for whom the test is intended.
    - date (str): The date of the test in date format.
    - period (int): The period or session for the test.
    - teacherName (str): The name of the teacher creating the test.

    Returns:
    - 201 Created: If the test is successfully added to the collection.
    - 400 Bad Request: If the JSON payload does not contain all the necessary fields or has invalid data types.
    """

    # checks the schema to verify or validate that all the necessary fields are given in the json file
    json_data = request.get_json()
    try:
        result = TestCreationRequestBodySchema().load(json_data)
    except ValidationError as err:  # throws an error instead of causing the whole program to break
        return '', 400  # bad request

    response = request.get_json()
    student = response["students"]
    listOfStudents = []
    for x in student:
        listOfStudents.append(
            ObjectId(x))  # Add the student IDs as strings into a list after turning them into ObjectIDs

    # adding the new test into the collection
    collectionTests.insert_one({
        "testName": response["testName"],
        "courseCode": response["courseCode"],
        "calculator": response["calculator"],
        "testLength": response["testLength"],
        "notes": response["notes"],
        "students": student,
        "date": response["date"],
        "period": response["period"],
        "startTime": [""] * len(response["students"]),
        "teacherName": response["teacherName"]
    })

    return '', 201  # created


@app.route("/test", methods=['DELETE'])
def delete_test():
    """Deletes a test from the 'tests' collection in the 'testApp' database by finding its ObjectID

    This route expects a JSON with the following field:
    - _id (str): The ID of the test to be deleted.

    Returns:
    - 200 OK: If the test is successfully deleted from the collection.
    """
    response = request.get_json()
    id = response["_id"]

    # finds the data with the given object ID and deletes it
    collectionTests.delete_one({
        "_id": ObjectId(id)
    })
    return '', 200  # OK


@app.route("/test", methods=['PATCH'])
def update_test():
    """
    Updates an existing test in the 'tests' collection of the 'testApp' database.

    This route expects a JSON payload with the following fields:
    - _id (str): The ID of the test to be updated.
    - testName (str): The updated name of the test.
    - courseCode (str): The updated course code for which the test is being created.
    - calculator (bool): Whether a calculator is allowed for the test.
    - testLength (int): The updated length of the test in minutes.
    - notes (str): Any additional notes or instructions for the test.
    - students (list of str): A list of updated student IDs for whom the test is intended.
    - date (str): The updated date of the test in date format.
    - period (int): The updated period or session for the test.
    - startTime (str): The updated start time of the test in HH:MM format.
    - teacherName (str): The updated name of the teacher creating the test.

    Returns:
    - 200 OK: If the test is successfully updated in the collection.
    - 400 Bad Request: If the JSON payload does not contain all the necessary fields or has invalid data types.
    """
    # checks the schema to verify or validate that all the necessary fields are given in the json file
    response = request.get_json()
    try:
        result = TestUpdateRequestBodySchema().load(response)
    except ValidationError as err:
        return '', 400  # bad request

    # expects all fields of a test to be given, even if it remains unchanged.
    id = response["_id"]
    student = response["students"]
    listOfStudents = []
    for x in student:
        listOfStudents.append(ObjectId(x))  # Convert student string ids into ObjectIDs

    collectionTests.update_one({"_id": ObjectId(id)},  # finds the test with the given ObjectID
                               {"$set": {"testName": response["testName"]}})  # changes a certain field
    collectionTests.update_one({"_id": ObjectId(id)},
                               {"$set": {"courseCode": response["courseCode"]}})
    collectionTests.update_one({"_id": ObjectId(id)},
                               {"$set": {"calculator": response["calculator"]}})
    collectionTests.update_one({"_id": ObjectId(id)},
                               {"$set": {"testLength": response["testLength"]}})
    collectionTests.update_one({"_id": ObjectId(id)},
                               {"$set": {"notes": response["notes"]}})
    collectionTests.update_one({"_id": ObjectId(id)},
                               {"$set": {"students": student}})
    collectionTests.update_one({"_id": ObjectId(id)},
                               {"$set": {"date": response["date"]}})
    collectionTests.update_one({"_id": ObjectId(id)},
                               {"$set": {"period": response["period"]}})
    collectionTests.update_one({"_id": ObjectId(id)},
                               {"$set": {"startTime": response["startTime"]}})
    collectionTests.update_one({"_id": ObjectId(id)},
                               {"$set": {"teacherName": response["teacherName"]}})
    return '', 200  # OK


@app.route("/test/start", methods=['PATCH'])
def update_testStartTime():
    """Updates the start time of an existing test in the 'tests' collection in the 'testApp' database.

    This route expects a JSON payload with the following fields:
    - _id (str): The ID of the test for which the start time is being updated.
    - startTime (str): The updated start time of the test in HH:MM format.

    Returns:
    - 200 OK: If the start time of the test is successfully updated in the collection.
    - 400 Bad Request: If the JSON payload does not contain all the necessary fields or has invalid data types.
    """
    # checks the schema to verify or validate that all the necessary fields are given in the json file
    response = request.get_json()
    try:
        result = TestUpdateTimeRequestBodySchema().load(response)
    except ValidationError as err:
        return '', 400  # Bad request

    id = response["_id"]

    collectionTests.update_one({"_id": ObjectId(id)},  # finds test with given ObjectID
                               {"$set": {"startTime": response["startTime"]}})  # updates start time only
    return '', 200  # OK


@app.route("/test", methods=['GET'])
def get_test():
    """Retrieves test data from the 'tests' collection in the 'testApp' database based on query parameters.

    Query Parameters:
    - testName (str): The name of the test to retrieve.
    - courseCode (str): The course code for which the test was created.
    - date (str): The date of the test in date format.
    - period (int): The period or session for the test.

    Returns:
    - 200 json_data, OK: A JSON array containing the test data that matches the query parameters.
    """
    # gets all the given query parameters
    testName = request.args.get('testName')
    courseCode = request.args.get('courseCode')
    date = request.args.get('date')
    period = request.args.get('period')

    # filters through the database, obtaining only the data that matches the query parameters
    query_filter = {}
    if testName is not None:
        query_filter["testName"] = testName
    if courseCode is not None:
        query_filter["courseCode"] = courseCode
    if period is not None:
        query_filter["period"] = period
    if date is not None:
        query_filter["date"] = date

    cursor = collectionTests.find(query_filter)

    # add all the found tests that matches the query parameters into a list
    data = []
    for doc in cursor:
        data.append(doc)

    # remove the $oid from each _id to simplify the process for the frontend
    json_data = []
    for doc in data:
        json_data.append(flatten_oid(doc))

    return json_data, 200  # OK


####################  Managing the student database  #######################

@app.route("/students", methods=['POST'])
def add_student():
    """Adds a new student to the 'students' collection in the 'testApp' database.

    This route expects a JSON payload with the following fields:
    - name (str): The name of the student.
    - email (str): The email address of the student.
    - extraTime (int): The amount of extra time (in minutes) the student is allowed for tests.

    Returns:
    - 201 Created: If the student is successfully added to the collection.
    - 400 Bad Request: If the JSON payload does not contain all the necessary fields or has invalid data types.
    """
    # checks the schema to verify or validate that all the necessary fields are given in the json file
    json_data = request.get_json()
    try:
        result = StudentCreationSchema().load(json_data)
    except ValidationError as err:
        return '', 400  # bad request

    response = request.get_json()

    collectionStudents.insert_one({  # adds the new student into the student collection
        "name": response["name"],
        "email": response["email"],
        "extraTime": response["extraTime"],

    })
    return '', 201  # Created


@app.route("/students", methods=['DELETE'])
def delete_student():
    """Deletes a student from the 'students' collection in the 'testApp' database.

    This route expects a JSON payload with the following field:
    - _id (str): The ID of the student to be deleted.

    Returns:
    - 200 OK: If the student is successfully deleted from the collection.
    """
    response = request.get_json()
    id = response["_id"]

    collectionStudents.delete_one({
        "_id": ObjectId(id)  # finds and deletes the student given their ObjectID
    })

    return '', 200  # OK


@app.route("/students", methods=['PATCH'])
def update_student():
    """Updates an existing student in the 'users' collection in the 'testApp' database.

    This route expects a JSON payload with the following fields:
    - _id (str): The ID of the student to be updated.
    - name (str): The updated name of the student.
    - email (str): The updated email address of the student.
    - extraTime (int): The updated amount of extra time (in minutes) the student is allowed for tests.

    Returns:
    - 200 OK: If the student is successfully updated in the collection.
    - 400 Bad Request: If the JSON payload does not contain all the necessary fields or has invalid data types.
    """
    # checks the schema to verify or validate that all the necessary fields are given in the json file
    response = request.get_json()
    try:
        result = StudentCreationSchema().load(response)
    except ValidationError as err:
        return '', 400  # Bad request

    id = response["_id"]
    collectionStudents.update_one({"_id": ObjectId(id)},  # finds the student using ID
                                  {"$set": {"name": response["name"]}})  # changes the fields
    collectionStudents.update_one({"_id": ObjectId(id)},
                                  {"$set": {"email": response["email"]}})
    collectionStudents.update_one({"_id": ObjectId(id)},
                                  {"$set": {"extraTime": response["extraTime"]}})
    return '', 200  # OK


@app.route("/students/extraTime", methods=['PATCH'])
def update_student_extraTime():
    """Updates a student's accommodation for a test (extra time)

    This route expects a list of JSONs with the following fields:
    - studentName: The name of the student whose extra time needs to be updated.
    - extraTime: the amount of extra time the student needs (As a Number)

    Returns:
    - 200 OK: If the course is successfully updated in the collection.
    - 400 Bad Request: If the JSON payload does not contain all the necessary fields or has invalid data types.
    """
    # checks the schema to verify or validate that an array of students is given
    response = request.get_json()
    try:
        result = StudentExtraTimeRequestBodySchemaArray().load(response)
    except ValidationError as err:
        return '', 400  # bad request

    # loops through all the jsons of students who need to have extra time
    for x in response:
        collectionStudents.updateOne({"name": x["name"]},
                                     {"$set": {"extraTime": x["name"]}})

    return '', 200  # OK


@app.route("/students", methods=['GET'])
def get_student():
    """Retrieves student data from the 'students' collection in the 'testApp' database based on query parameters.

    Query Parameters:
    - name (str): The name of the student to retrieve.
    - email (str): The email address of the student to retrieve.
    - extraTime (int): The amount of extra time (in minutes) the student is allowed for tests.

    Returns:
    - 200 OK: A JSON array containing the student data that matches the query parameters.
    """
    # gets all the given query parameters
    name = request.args.get('name')
    email = request.args.get('email')
    extraTime = request.args.get('extraTime')
    id = request.args.get('_id')

    # filters through the database, obtaining only the information that matches the query parameters
    query_filter = {}
    if name is not None:
        query_filter["name"] = name
    if email is not None:
        query_filter["email"] = email
    if extraTime is not None:
        query_filter["extraTime"] = extraTime
    if id is not None:
        query_filter["_id"] = id

    cursor = collectionStudents.find(query_filter)

    # add all the found students that matches the query parameters into a list
    data = []
    for doc in cursor:
        data.append(doc)

    # removes the $oid from each _id to simplify the processes in the frontend
    json_data = []
    for doc in data:
        json_data.append(flatten_oid(doc))

    return json_data, 200  # OK


####################  Managing the course database  #######################

@app.route("/course", methods=['POST'])
def add_course():
    """
    Adds a new course to the 'courses' collection in the 'testApp' database.

    This route expects a JSON payload with the following fields:
    - courseName (str): The name of the course.
    - students (list of str): A list of student IDs enrolled in the course.

    Returns:
    - 201 Created: If the course is successfully added to the collection.
    - 400 Bad Request: If the JSON payload does not contain all the necessary fields or has invalid data types.
    """
    # checks the schema to verify or validate that all the necessary fields are given in the json file
    json_data = request.get_json()
    try:
        result = CourseCreationRequestBodySchema().load(json_data)
    except ValidationError as err:
        return '', 400  # bad request
    response = request.get_json()

    student = response["students"]
    listOfStudents = []
    for x in student:
        listOfStudents.append(ObjectId(x))  # turn the strings of student ids into ObjectIDs and stores them into a list

    collectionCourses.insert_one({  # adding the new course into the collection
        "courseName": response["courseName"],
        "students": listOfStudents
    })

    return '', 201  # Created


@app.route("/course", methods=['DELETE'])
def delete_course():
    """Deletes a course from the 'courses' collection in the 'testApp' database.

    This route expects a JSON payload with the following field:
    - _id (str): The ID of the course to be deleted.

    Returns:
    - 200 OK: If the course is successfully deleted from the collection.
    """
    response = request.get_json()
    id = response["_id"]

    collectionCourses.delete_one({
        "_id": ObjectId(id)  # finds course based on ObjectID and deletes it
    })

    return '', 200  # OK


@app.route("/course", methods=['PATCH'])
def update_course():
    """
    Updates an existing course in the 'courses' collection in the 'testApp' database.

    This route expects a JSON payload with the following fields:
    - _id (str): The ID of the course to be updated.
    - courseName (str): The updated name of the course.
    - students (list of str): A list of updated student IDs enrolled in the course.

    Returns:
    - 200 OK: If the course is successfully updated in the collection.
    - 400 Bad Request: If the JSON payload does not contain all the necessary fields or has invalid data types.
    """
    # checks the schema to verify or validate that all the necessary fields are given in the json file
    response = request.get_json()
    try:
        result = CourseCreationRequestBodySchema().load(response)
    except ValidationError as err:
        return '', 400  # bad request

    student = response["students"]
    listOfStudents = []
    for x in student:
        listOfStudents.append(ObjectId(x))  # Given list of student ids as strings, add them to list as ObjectIDs

    id = response["_id"]
    collectionCourses.update_one({"_id": ObjectId(id)},  # finds by ObjectId
                                 {"$set": {"courseName": response["courseName"]}})  # change fields
    collectionCourses.update_one({"_id": ObjectId(id)},
                                 {"$set": {"students": listOfStudents}})
    return '', 200  # OK


@app.route("/course", methods=['GET'])  # method used in insomnia
def get_course():
    """Retrieves course data from the 'courses' collection in the 'testApp' database based on query parameters.

    Query Parameters:
    - courseName (str): The name of the course to retrieve.

    Returns:
    - 200 OK: A JSON array containing the course data that matches the query parameters.
    """
    # gets course name from given query parameter
    courseName = request.args.get('courseName')
    id = request.args.get('_id')

    # filters through the database, obtaining only the information that matches the query parameters
    query_filter = {}
    if courseName is not None:
        query_filter["courseName"] = courseName
    if id is not None:
        query_filter["_id"] = id

    cursor = collectionCourses.find(query_filter)

    # add all the found courses that matches the query parameters into a list
    data = []
    for doc in cursor:
        data.append(doc)

    # removes the $oid from each _id to simplify the processes for the frontend
    json_data = []
    for doc in data:
        json_data.append(flatten_oid(doc))

    return json_data, 200  # OK


####################  Authentication #######################

@app.route("/entra-id/flow", methods=['GET'])
def get_consent_form_url():
    """This route generates a state document in the MongoDB collection 'OAuthStates.'

    Returns:
    - Redirects the user to the Microsoft Azure Active Directory login page for consent.
    """
    # create a state document in mongodb
    state_token = str(uuid4())
    collectionOAuthStates.insert_one({
        "state": state_token,
        "status": "pending"
    })

    return redirect(
        f"https://login.microsoftonline.com/{environ.get("ENTRA_TENANT_ID")}/oauth2/v2.0/authorize?client_id={environ.get('ENTRA_CLIENT_ID')}&response_type=code&redirect_uri={environ.get('ENTRA_REDIRECT_URI')}&response_mode=query&scope=User.Read&state={state_token}")


@app.route("/entra-id/flow", methods=['POST'])
def authenticate_user():
    """Authenticates the user using the OAuth 2.0 authorization code flow with Microsoft Azure Active Directory
    It first verifies the state token provided in the request JSON payload with the state token stored in the 'OAuthStates' collection in MongoDB
    It then exchanges the authorization code for an OAuth token and retrieves
    user information from Microsoft Graph API. If successful, it creates a session token and sets a session cookie.

    Returns:
    - 200 OK: If the user is successfully authenticated and a session cookie is set.
    - 400 Bad Request: If there is an error in the authentication process or the state token is invalid.
    - 500 Internal Server Error: If there is an issue updating the state token in the database.
    """
    # verify state token
    state_token = request.get_json()["state"]
    state = collectionOAuthStates.find_one({"state": state_token})
    if state is None:
        return json.dumps({"error": "Invalid state token"}), 400

    if state["status"] != "pending":
        return json.dumps({"error": "State token has already been used"}), 400

    # get oauth token 
    try:
        resp = requests.post(f"https://login.microsoftonline.com/{environ.get("ENTRA_TENANT_ID")}/oauth2/v2.0/token",
                             data={
                                 "client_id": environ.get("ENTRA_CLIENT_ID"),
                                 "client_secret": environ.get("ENTRA_CLIENT_SECRET"),
                                 "code": request.get_json()["code"],
                                 "redirect_uri": environ.get("ENTRA_REDIRECT_URI"),
                                 "grant_type": "authorization_code",
                                 "scope": "User.Read"
                             })
        resp.raise_for_status()
        access_token = resp.json()["access_token"]
    except requests.exceptions.HTTPError as e:
        return json.dumps({"error": "Failed to authenticate user"}), 400

    # get user info
    try:
        resp = requests.get("https://graph.microsoft.com/v1.0/me", headers={
            "Authorization": f"Bearer {access_token}"
        })
        resp.raise_for_status()
        user_info = resp.json()
    except requests.exceptions.HTTPError as e:
        return json.dumps({"error": "Failed to get user info"}), 400

    # set state token to used
    try:
        collectionOAuthStates.update_one({"state": state_token}, {"$set": {"status": "used"}})
    except:
        return json.dumps({"error": "Failed to update state token"}), 500

    # create a session document in mongodb
    session_token = str(uuid4())
    role = "teacher"
    if "Student" in user_info["jobTitle"]:
        role = "student"

    collectionSessions.insert_one({
        "session": session_token,
        "role": role,
    })

    resp = make_response("Logged in")
    resp.set_cookie("session", session_token)


# Runs the whole application
if __name__ == "__main__":
    app.run(debug=environ.get("DEBUG") == "true", port=3000, host=environ.get("HOST") or "127.0.0.1")
