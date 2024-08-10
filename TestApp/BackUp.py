"""
This initializes a connection to a MongoDB database using MongoClient and sets up a Flask application with CORS enabled.

Usage:
1. Initialize a connection to a MongoDB database running on localhost and port 27017.
2. Access the 'testApp' database and its collections: 'tests', 'users', and 'courses'.
3. Create a Flask application instance and enable CORS (Cross-Origin Resource Sharing) for the app.

Note: Ensure that the MongoDB server is running on localhost and listening on port 27017 before using this script.
"""
from flask import Flask, request
from pymongo import MongoClient
import bson.objectid
from bson.objectid import ObjectId
from marshmallow import Schema, fields, ValidationError
from flask_cors import CORS

# connecting to the MongoDB server using localhost
client = MongoClient("localhost", 27017)

# getting the database and its collections
db = client.testApp
collectionTests = db.tests
collectionStudents = db.users
collectionCourses = db.courses

app = Flask(__name__)  # Initialize the Flask application
cors = CORS(app)  # Enable CORS for the Flask app


def handle_object_id(obj):
    """This method converts the obj into a string if the given obj is an instance of bson.ObjectId

    :param obj: The object to be converted
    :return: The string representation of the object if it is an instance of bson.ObjectId
    :raise: TypeError if the obj is not an instance of bson.ObjectId.
    """
    if isinstance(obj, bson.ObjectId):
        return str(obj)
    return TypeError


class TestCreationRequestBodySchema(Schema):
    """Schema for validating the request body when creating a new test.
    This lists all the required fields that needs to be included so that a test can be created

    :param testName: The name of the test. Required.
    :param courseCode: The course code for which the test is being created. Required.
    :param calculator: Whether a calculator is permitted for the test. Required, should be a boolean value.
    :param testLength: The length of the test in minutes. Required, should be a number.
    :param notes: Any additional notes or instructions for the test. Required.
    :param students: A list of student IDs for whom the test is intended. Required, each ID should be a string.
    :param date: The date of the test. Required, should be a date in YYYY-MM-DD format.
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
    This lists all the required fields that needs to be included so that a test can be updated

    :param _id: The ID of the test to be updated. Required.
    :param testName: The updated name of the test. Required.
    :param courseCode: The updated course code for which the test is being created. Required.
    :param calculator: Whether a calculator is allowed for the test. Required, should be a boolean value.
    :param testLength: The updated length of the test in minutes. Required, should be a number.
    :param notes: Any additional notes or instructions for the test. Required.
    :param students: A list of student IDs for whom the test is intended. Required, each ID should be a string.
    :param date: The updated date of the test. Required, should be a date in YYYY-MM-DD format.
    :param period: The updated period or session for the test. Required, should be a number.
    :param startTime: The updated start time of the test. Required, should be a string in HH:MM format.
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
    """Schema for validating the request body when creating a student.

    :param studentName: The name of the student. Required.
    :param email: The email address of the student. Required.
    :param extraTime: The amount of extra time (min) the student is allowed for tests. Required, should be a number.
    """
    studentName = fields.Str(required=True)
    email = fields.Str(required=True)
    extraTime = fields.Number(required=True)


class TestUpdateTimeRequestBodySchema(Schema):
    """Schema for validating the request body when updating the start time of a test.

    :param _id: The ID of the test for which the start time is being updated. Required.
    :param startTime: The updated start time of the test. Required, should be a string in HH:MM format.
    """
    _id = fields.Str(required=True)
    startTime = fields.Str(required=True)


class CourseCreationRequestBodySchema(Schema):
    """Schema for validating the request body when creating a course.

    :param courseName: The name of the course. Required.
    :param students: A list of student IDs enrolled in the course. Required, each ID should be a string.
    """
    courseName = fields.Str(required=True)
    students = fields.List(fields.Str, required=True)


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
    - date (str): The date of the test in YYYY-MM-DD format.
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
        listOfStudents.append(ObjectId(x))  # Given list of students as strings. Add to list as ObjectIDs

    # adding the test into the collection
    collectionTests.insert_one({
        "testName": response["testName"],
        "courseCode": response["courseCode"],
        "calculator": response["calculator"],
        "testLength": response["testLength"],
        "notes": response["notes"],
        "students": listOfStudents,
        "date": response["date"],
        "period": response["period"],
        "startTime": [""]*len(response["students"]),
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

    collectionTests.delete_one({
        "_id": ObjectId(id)
    })
    return '', 200  # OK


@app.route("/test", methods=['PATCH'])
def update_test():
    """
    Updates an existing test in the 'tests' collection in the 'testApp' database.

    This route expects a JSON payload with the following fields:
    - _id (str): The ID of the test to be updated.
    - testName (str): The updated name of the test.
    - courseCode (str): The updated course code for which the test is being created.
    - calculator (bool): Whether a calculator is allowed for the test.
    - testLength (int): The updated length of the test in minutes.
    - notes (str): Any additional notes or instructions for the test.
    - students (list of str): A list of updated student IDs for whom the test is intended.
    - date (str): The updated date of the test in YYYY-MM-DD format.
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

    # expects all fields of a test to be given, even if not changed.
    id = response["_id"]
    student = response["students"]
    listOfStudents = []
    for x in student:
        listOfStudents.append(ObjectId(x))  # Given list of students as strings. Add to list as ObjectIDs

    collectionTests.update_one({"_id": ObjectId(id)},  # finds test with given ObjectID
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
                               {"$set": {"students": listOfStudents}})
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
    """
    Updates the start time of an existing test in the 'tests' collection in the 'testApp' database.

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


def flatten_oid(obj):
    """
    Converts the "_id" field of a dictionary to a string and stores it in a new "id" field,
    then removes the "_id" field from the dictionary. This is meant to remove the embedded $oid

    :param obj: A dictionary containing an "_id" field to be flattened.
    :return: The new _id without embedded $oid
    """
    old_id = obj["_id"]
    obj["id"] = str(old_id)
    del obj["_id"]
    return obj


@app.route("/test", methods=['GET'])
def get_test():
    """
    Retrieves test data from the 'tests' collection in the 'testApp' database based on query parameters.

    Query Parameters:
    - testName (str): The name of the test to retrieve.
    - courseCode (str): The course code for which the test was created.
    - date (str): The date of the test in YYYY-MM-DD format.
    - period (int): The period or session for the test.

    Returns:
    - 200 OK: A JSON array containing the test data that matches the query parameters.
    """
    # gets all the given query parameters
    testName = request.args.get('testName')
    courseCode = request.args.get('courseCode')
    date = request.args.get('date')
    period = request.args.get('period')

    # filters, obtaining only the information that matches the query parameters
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

    # removes the $oid from each _id
    json_data = []
    for doc in data:
        json_data.append(flatten_oid(doc))

    return json_data, 200  # OK


@app.route("/students", methods=['POST'])
def add_student():
    """
    Adds a new student to the 'users' collection in the 'testApp' database.

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

    collectionStudents.insert_one({  # add new student into the student collection
        "name": response["name"],
        "email": response["email"],
        "extraTime": response["extraTime"],

    })
    return '', 201  # Created


@app.route("/students", methods=['DELETE'])
def delete_student():
    """
    Deletes a student from the 'users' collection in the 'testApp' database.

    This route expects a JSON payload with the following field:
    - _id (str): The ID of the student to be deleted.

    Returns:
    - 200 OK: If the student is successfully deleted from the collection.
    """
    response = request.get_json()
    id = response["_id"]

    collectionStudents.delete_one({
        "_id": ObjectId(id)  # deletes student given ObjectID
    })

    return '', 200  # OK


@app.route("/students", methods=['PATCH'])
def update_student():
    """
    Updates an existing student in the 'users' collection in the 'testApp' database.

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


@app.route("/students", methods=['GET'])
def get_student():
    """
    Retrieves student data from the 'users' collection in the 'testApp' database based on query parameters.

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

    # filters, obtaining only the information that matches the query parameters
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

    # removes the $oid from each _id
    json_data = []
    for doc in data:
        json_data.append(flatten_oid(doc))

    return json_data, 200  # OK


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

    # given a list of students, as their ObjectIDs, in strings
    student = response["students"]
    listOfStudents = []
    for x in student:
        listOfStudents.append(ObjectId(x))  # turn the strings into ObjectIDs and store into a list

    collectionCourses.insert_one({  # adding course into a collection
        "courseName": response["courseName"],
        "students": listOfStudents
    })

    return '', 201  # Created


@app.route("/course", methods=['DELETE'])
def delete_course():
    """
    Deletes a course from the 'courses' collection in the 'testApp' database.

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
        listOfStudents.append(ObjectId(x))  # Given list of students as strings. Add to list as ObjectIDs

    id = response["_id"]
    collectionCourses.update_one({"_id": ObjectId(id)},  # finds by ObjectId
                                 {"$set": {"courseName": response["courseName"]}})  # change fields
    collectionCourses.update_one({"_id": ObjectId(id)},
                                 {"$set": {"students": listOfStudents}})
    return '', 200  # OK


@app.route("/course", methods=['GET'])  # method used in insomnia
def get_course():
    """
    Retrieves course data from the 'courses' collection in the 'testApp' database based on query parameters.

    Query Parameters:
    - courseName (str): The name of the course to retrieve.

    Returns:
    - 200 OK: A JSON array containing the course data that matches the query parameters.
    """
    # gets course name from given query parameter
    courseName = request.args.get('courseName')
    id = request.args.get('_id')

    # filters, obtaining only the information that matches the query parameters
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

    # removes the $oid from each _id
    json_data = []
    for doc in data:
        json_data.append(flatten_oid(doc))

    return json_data, 200  # OK


@app.route("/upload", methods=['POST'])
def upload():
    """
    Uploads student and course data to the 'users' and 'courses' collections in the 'testApp' database.

    This route expects a JSON payload with the following structure:
    [
        {
            "studentName": "Name of the student",
            "email": "Email of the student",
            "courseName": "Name of the course"
        },
        ...
    ]
    Returns:
    - 201 Created: If the data is successfully uploaded to the collections.
    """
    response = request.get_json()

    # using a set, add all the students from the given file and upload them into the database
    student_data = set(
        (data["studentName"], data["email"]) for data in response)      # for loop, adds all students

    students = [{                                   # adds all the data of a student into a list
        "name": data[0],
        "email": data[1],
        "extraTime": 0
    } for data in student_data]

    collectionStudents.insert_many(students)        # inserts all the students into the collection

    # Does the same thing for uploading all the courses
    course_data = set(data["courseName"] for data in response)
    courses = [{
        "courseName": data,
        "students": [],
    } for data in course_data]

    collectionCourses.insert_many(courses)

    return "", 201  # Created


if __name__ == "__main__":
    app.run(debug=True, port=3000)
