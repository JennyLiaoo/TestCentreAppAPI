<a name="readme-top"></a>
<br />

<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
  </a>

  <h3 align="center">README</h3>

  <p align="center">
    This is a readme file.
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
   <li><a href="#configuring-your-environment">Configuring your environment</a></li>
    <li><a href="#how-to-use-and-usages">How to Use and Usages</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

The current process for scheduling students into the Test Center and handling accommodations
is inefficient and time-consuming for all parties involved. The accommodation information is stored in an Excel
spreadsheet on SharePoint and is not easily accessible to the Test Center Coordinator. The planned web application aims to address these challenges by streamlining the scheduling
process and reducing reliance on email communication. This part of the project focuses on the backend of the application, where the system receives information and data from the frontend to be managed and stored into a database.

- The student name, email, and any accommodations are stored in the student database.
- The test name, course code, test length, additional notes, the test date, the period, the teacher, calculator permission, and the list of the students taking the test are stored in the test database.
- The course name, and the list of students taking the course are stored in the course database

This application is able to retain collected data, and provide an easy way to digitize existing records. It can store and manage student, test, and course information, and allow for creating, deleting, updating, and retrieving of data from the databases.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

- [![Flask][Flask.js]][Flask-url]
- [![MongoDB][MongoDB.js]][MongoDB-url]
- [![Python][Python.js]][Python-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

This project is written in Python (Version 3) using PyCharm. It uses Flask as a web framework, which allows for the development of web applications using Python. Flask-Marshmallow, a thin integration layer for Flask, is used to create Schemas to validate the given fields in a request body, and Flask-CORS is used to support cross-origin resource sharing. This system uses PyMongo, a python library, to connect to MongoDB, a NoSQL database used to store large amounts of data.
</br> </br>
Some additional software used in the development of this project includes Insomnia, which was used to debug and test the API locally, and Docker, which was used to run the application.

### Prerequisites


For this project, you will need to install Flask, PyMongo, Marshmallow, Flask-CORS, and a couple more packages. Through PyCharm, you should be given the option to install the packages when you try to import the libraries found at the top of this project.
<br/><br/>
**Recommended**: An alternative option is to simply run `pip3 install -r requirements.txt`. This file also contains all the libraries you need to get started with this project.

### Installation

Below are links showing how to install the additional software used to either create or test the project.

1. PyCharm: [https://www.jetbrains.com/help/pycharm/installation-guide.html](https://www.jetbrains.com/help/pycharm/installation-guide.html)
2. MongoDB: [https://www.mongodb.com/docs/manual/installation/](https://www.mongodb.com/docs/manual/installation/)
3. Insomnia: [https://docs.insomnia.rest/insomnia/install](https://docs.insomnia.rest/insomnia/install)
4. Docker: [https://www.docker.com/get-started/](https://www.docker.com/get-started/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Configuring your environment

Virtual environments are lightweight, self-contained Python installations, designed to be set up without requiring extensive configuration or specialized knowledge. This avoids the need to install Python packages globally; they will only be installed within the environment. It's recommended to use a Python venv (Creation of virtual environments). To create a venv, run the following command in your terminal:

```sh
python3 -m venv venv
```

To activate the venv, run the following command in your terminal:

```sh
source venv/bin/activate
```

To deactivate the venv, run the following command in your terminal:

```sh
deactivate
```

You should configure your `.env` file, which has variables to configure the application. By default, if your MongoDB is unauthenticated and runs on localhost:27017, it should run without configuration. However, if your MongoDB setup is different, you should copy `.env.example` to `.env` and change the values accordingly.

<!-- USAGE EXAMPLES -->

## How to Use and Usages

@app.route is a decorator in Flask which is used to bind a URL to a method. When a specific URL is requested, Flask knows to call the method below it. For example, there could be multiple delete methods. We would distinguish them based on their URL ("/test" for deleting tests, "/students" for deleting students, etc.).

There are a couple of main methods that are used throughout this system, simply applied a bit differently each time. Firstly, there is POST, which adds to the database based on what is given in the request body. This is validated by a schema before the action is performed. Secondly, DELETE, which deletes from the database when given a specific _id to find. Thirdly, there is PATCH, which updates the database based on the request body. This is also validated using a schema. And lastly, GET, which retrieves data from the database. It does this by filtering the database to find data that matches the given query parameters.

As previously mentioned, schemas are used to validate the request body. If I need certain pieces of data to, for example, create a new test, I would use a schema to check if I receive everything I need in the JSON file. The schemas ensure that if the backend somehow doesn't receive the right information, the system would simply throw an error rather than break entirely.

The code is structured in the following sections:

1. Setting Up:
   - This section contains all the libraries that need to be imported, the code that connects to the MongoDB database and its collections, and it initializes the Flask application while enabling CORS.
2. Helper Methods:
   - These methods help make the information received by the frontend easier to manage.
3. Schemas
   - This section consists of the schemas needed to validate the request body when making a change (PATCH), or adding a new entry into the database (POST).
4. Upload
   - The initial bulk upload of all the students and courses into the database. This uses the POST method.
5. Managing the test database
   - This section has the add test (POST), delete test (DELETE), update test (PATCH), update start time (PATCH), and get test (GET) methods.
6. Managing the student database
   - This has the add student (POST), delete student (DELETE), update student (PATCH), update student extra time (PATCH), and get student (GET) methods.
7. Managing the course database
   - This consists of the add course (POST), delete course (DELETE), update course (PATCH), and get course (GET) methods.
8. Authentication
   - This integrates Microsoft Azure Active Directory for user authentication. It creates a unique state token that is stored in a MongoDB collection. It then redirects the user to the Microsoft AAD login page, where the user can consent to the application accessing their information.
   - Then, it verifies the state token received from the user against the token stored in the collection. If it is valid, the system exchanges the authorization code for an OAuth token with AAD. It retrieves the user information, creates a session token for the user, and sets a session cookie allowing the user to remain logged in.
 
   <p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTACT -->

## Contact

Adam Drenth - adam.drenth@ashbury.ca


<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com
[Flask.js]: https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white
[Flask-url]: https://flask.palletsprojects.com/en/3.0.x/
[MongoDB.js]: https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white
[MongoDB-url]: https://www.mongodb.com/cloud/atlas/lp/try4?utm_source=google&utm_campaign=search_gs_pl_evergreen_atlas_core_retarget-brand_gic-null_amers-us-ca_ps-all_desktop_eng_lead&utm_term=mongodb&utm_medium=cpc_paid_search&utm_ad=e&utm_ad_campaign_id=14291004479&adgroup=128837427347&cq_cmp=14291004479&gad_source=1&gclid=CjwKCAjwtqmwBhBVEiwAL-WAYV2RYDs_51kMsS17Uje1Z0sz9du9xeTBmz8Djmp0r7oHFz28BTfBKxoCrKIQAvD_BwE
[Python.js]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/

