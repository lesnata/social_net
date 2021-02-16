## Table of contents
* [General info](#general-info)
* [Routes](#routes)
* [Postman collection](#postman-collection)
* [Technologies](#technologies)
* [Style conventions](#style-conventions)
* [Setup](#setup)

## General info
The app introduces an Social networking app with Post and Like objects,
empowered with JWT token permissions.
Basic Features:
- user signup
- user login
- post creation
- post like
- post unlike
- analytics about how many likes was made, analytics aggregated by day.
- user activity an endpoint, which shows the last login time of user
and when he made a last request to the service.



## Routes
- api/account/register, views.registration [Registration]
- api/token/, [Login]
- post/, views.post_collection, [GET, POST posts]
- post/<int:id>, views.post_element [GET. PUT, DELETE post] 
- post/<int:id>/like, views.post_like [Post like/unlike]
- analytics/, views.analytics [Analytics of likes]
- user-activity/, views.user_activity [User activity]


## Postman collection
Postman collection link: 
https://www.getpostman.com/collections/7d056935cd99a50194c7

## Technologies
Project is created with:
* Django==3.1.6
* djangorestframework==3.12.2
* djangorestframework-simplejwt==4.6.0
* black==20.8b1
* flake8==3.8.4


## Style conventions
For code conventions used Black and Flake8 library. 
All functions and model methods have explicit doc strings explanations.


## Setup
To run this project locally, make the following:

```
$ git clone https://github.com/lesnata/social_net.git
$ cd social_net
$ virtualenv venv_social
$ source venv_social/bin/activate
$ (venv_social)$ pip install -r requirements.txt
$ (venv_social)$ python manage.py runserver
```

You may enter as a user via admin panel:
```
Tokio
tokio-tomato-1
```

