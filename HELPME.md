# Django Fullstack Developer Capstone - Setup Guide

## Table of Contents
1. [Project Setup](#project-setup)
2. [Static Pages](#static-pages)
3. [Authentication System](#authentication-system)
4. [Registration System](#registration-system)

---

## Project Setup

### Folder Structure Overview

The Django app skeleton contains a `server` folder with three main sub-folders:

* **`djangoapp`**: Django application code
* **`djangoproj`**: Project configuration files  
* **`frontend`**: HTML, CSS, and React components

### Prerequisites

- Python 3.8+
- Django framework (`pip install django`)
- Project dependencies (`pip install -r requirements.txt`)

### Running the Development Server

1. **Navigate to project directory:**
   ```bash
   cd server/djangoproj
   ```

2. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Create superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

4. **Start development server:**
   ```bash
   python manage.py runserver
   ```

### Application URLs

- **Main Application**: `http://127.0.0.1:8000/`
- **Admin Panel**: `http://127.0.0.1:8000/admin/`
- **API Endpoints**: Check `urls.py` for configured routes

---

## Static Pages

### About Us Page

1. **Create About.html template** in `server/frontend/static/`

2. **Add stylesheets:**
   ```html
   <link rel="stylesheet" href="/static/style.css">
   <link rel="stylesheet" href="/static/bootstrap.min.css">
   ```

3. **Configure URL routing** in `djangoproj/urls.py`:
   ```python
   from django.views.generic import TemplateView
   
   urlpatterns = [
       path('about/', TemplateView.as_view(template_name="About.html")),
   ]
   ```

### Contact Us Page

1. **Create Contact.html template** with contact form
2. **Add background image** and modern styling
3. **Configure URL routing** similar to About page

---

## Authentication System

### Login Functionality

#### Backend Setup

1. **Update `djangoapp/views.py`:**
   ```python
   @csrf_exempt
   def login_user(request):
       if request.method == 'POST':
           data = json.loads(request.body)
           username = data['userName']
           password = data['password']
           user = authenticate(username=username, password=password)
           data = {"userName": username}
           if user is not None:
               login(request, user)
               data = {"userName": username, "status": "Authenticated"}
           return JsonResponse(data)
       else:
           return JsonResponse({"error": "POST method required"})
   ```

2. **Configure URLs in `djangoapp/urls.py`:**
   ```python
   path(route='login', view=views.login_user, name='login'),
   ```

3. **Add main URL route in `djangoproj/urls.py`:**
   ```python
   path('login/', TemplateView.as_view(template_name="login.html")),
   ```

#### Frontend Setup

1. **Create login.html template** with form
2. **Add JavaScript for authentication**
3. **Handle session storage**

### Logout Functionality

#### Backend Setup

1. **Add logout view to `djangoapp/views.py`:**
   ```python
   def logout_request(request):
       logout(request)  # Terminate user session
       data = {"userName": ""}  # Return empty username
       return JsonResponse(data)
   ```

2. **Configure URL routing:**
   ```python
   path(route='logout', view=views.logout_request, name='logout'),
   ```

#### Frontend Setup

1. **Add logout JavaScript to Home.html:**
   ```javascript
   const logout = async (e) => {
     let logout_url = window.location.origin + "/djangoapp/logout";
     const res = await fetch(logout_url, { method: "GET" });
     const json = await res.json();
     if (json) {
       let username = sessionStorage.getItem('username');
       alert("Logging out " + username + "...");
       sessionStorage.removeItem('username');
       window.location.href = window.location.origin;
     }
   };
   ```

---


## Registration System

### Backend Implementation

1. **Add registration view to `djangoapp/views.py`:**
   ```python
   @csrf_exempt
   def registration(request):
       if request.method != 'POST':
           return JsonResponse({'error': 'Only POST method allowed'}, status=405)
       
       data = json.loads(request.body)
       username = data['userName']
       password = data['password']
       first_name = data['firstName']
       last_name = data['lastName']
       email = data['email']
       
       # Check if user already exists
       if User.objects.filter(username=username).exists():
           return JsonResponse({'error': 'Username already exists'}, status=400)
       
       # Create user
       user = User.objects.create_user(
           username=username,
           first_name=first_name,
           last_name=last_name,
           password=password,
           email=email
       )
       
       # Login the user
       login(request, user)
       
       return JsonResponse({
           'userName': username,
           'status': 'Authenticated'
       })
   ```

2. **Configure URL routing:**
   ```python
   path('register/', views.registration, name='register'),
   ```

### Frontend Implementation

1. **Create register.html template** with modern UI
2. **Add form validation** and error handling
3. **Implement JavaScript** for form submission
4. **Handle registration success** with redirect

### Required Imports

```python
import json
import logging
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)
```

---

## Development Notes

- Use `Ctrl+C` to stop the development server
- Server automatically reloads on code changes
- Check browser console for JavaScript errors
- Verify static files configuration in `settings.py`
- Test all functionality in different browsers

# Working with Mongoose to provide API endpoints

## Setup and Initial Configuration

1. Open a new terminal and clone your project from GitHub if the environment has been reset.

2. Change to the directory with the data files:

```bash
cd /home/project/xrwvm-fullstack_developer_capstone/server/database
```

## Project Overview

For your online course lab project, you have been provided two schema files for Reviews and Dealerships entities, along with JSON files containing dealership and review data to be loaded into MongoDB and served through endpoints.

**Data Files:**
* `server/database/data/dealerships.json`
* `server/database/data/reviews.json`

## Schema and Database Integration

1. The Node app will use `mongoose` to interact with the MongoDB. The schemas for Reviews and Dealerships are defined in `review.js` and `dealership.js`, respectively.

2. View the content in `server/database/app.js`. It will provide the following endpoints:

   * **fetchReviews** - for fetching all reviews
   * **fetchReviews/dealer/:id** - for fetching reviews of a particular dealer
   * **fetchDealers** - for fetching all dealerships
   * **fetchDealers/:state** - for fetching all dealerships in a particular state
   * **fetchDealer/:id** - for dealer by id
   * **insert_review** - for inserting reviews

   Some of the endpoints have been implemented for you. Use the ideas and prior learning to implement the endpoints that are not implemented.

## Building and Running the Application

3. Run the following command to build the Docker app. Remember to do this every time you make changes to `app.js`:

```bash
docker build . -t nodeapp
```

> **Note:** The first time you build, it takes up to two minutes to successfully build.

4. The `docker-compose.yml` has been created to run two containers, one for Mongo and the other for the Node app. Run the following command to run the server:

```bash
docker-compose up
```

5. When you see the output on the terminal as shown in the following image, it would mean that the server has successfully started, and you can connect to it.

## Implementation Tasks

Your task is to complete the missing endpoint implementations in the `app.js` file using the provided schemas and following the patterns established in the already implemented endpoints.


# Create API Endpoint URLs

## Implementation Tasks

1. Implement the following endpoints that are yet to be implemented in `server/database/app.js`:
   * **fetchDealers** - for fetching all dealerships
   * **fetchDealers/:state** - for fetching dealerships by state
   * **fetchDealer/:id** - for fetching a specific dealer by ID

## Deployment and Testing Setup

2. Stop your Docker application that you started in the previous task.

3. Execute the `docker build` and `docker compose` commands again:

```bash
docker build . -t nodeapp
docker-compose up
```

4. Click `Fetch Reviews` below to test all endpoints by replacing the route in the address bar.

**Fetch Reviews**

## Testing Requirements

5. Test the following endpoints, take a screenshot of each, and save as specified:

### Required Screenshots

* **`/fetchReviews/dealer/29`** 
  - Save the screenshot as `dealer_review.png` or `dealer_review.jpg`
  - This endpoint fetches reviews for dealer with ID 29

* **`/fetchDealers`** 
  - Save the screenshot as `dealerships.png` or `dealerships.jpg`
  - This endpoint fetches all dealerships

* **`/fetchDealer/3`** 
  - Save the screenshot as `dealer_details.png` or `dealer_details.jpg`
  - This endpoint fetches details for dealer with ID 3

* **`/fetchDealers/Kansas`** 
  - Save the screenshot as `kansasDealers.png` or `kansasDealers.jpg`
  - This endpoint fetches all dealerships in Kansas state

## Final Steps

6. Push the updated `app.js` code to your GitHub repository.

## Testing Checklist

- [ ] Implement fetchDealers endpoint
- [ ] Implement fetchDealers/:state endpoint  
- [ ] Implement fetchDealer/:id endpoint
- [ ] Rebuild Docker container
- [ ] Test all endpoints and capture screenshots
- [ ] Save screenshots with correct filenames
- [ ] Push code changes to GitHub

# Django Models Views

## Overview

You have created a dealership and reviews related to CRUD APIs. Next, you need to create data models and services for the dealers' inventory. Each dealer manages a car inventory with different car models and makes, which are, in fact, relatively static data, thus suitable to be stored in Django locally.

To integrate external dealers and review data, you will need to call the APIs from the Django app and process the API results in Django views to be later rendered through REACT pages. Such Django views use proxy services to fetch data from external resources as per users' requests and renders it using REACT components.

## Tasks Overview

In this lesson, you need to perform the following tasks to add car model and make related models and views, and proxy services:

* Create CarModel and CarMake Django models
* Register CarModel and CarMake models with the admin site  
* Create new car models objects with associated car makes and dealerships

Follow the instructional lab to complete the above tasks step by step.

---

# Build CarModel and CarMake Django Models

**Estimated time needed:** 90 minutes

A dealership typically manages cars from one or more makers or manufacturers, and customers should be allowed to review the cars they purchased from a dealer.

In this lab, you will create the `CarModel` and `CarMake` models in the Django app.

* A **car model** includes basic information such as its make, year, type, and dealer id.
* A **car make** includes basic information such as name and description.

## Steps to Build CarModel and CarMake models

You will need to create two new models in `server/djangoapp/models.py`:
* A `CarMake` model to save some data about a car's make.
* A `CarModel` model to save some data about a car's model.

### 1. Create CarMake Django Model

Create a car make Django model `class CarMake(models.Model)`:
* Name
* Description  
* Any other fields you would like to include in a car make
* A `__str__` method to print a car make object

**Sample Implementation:**

```python
class CarMake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    # Other fields as needed
    
    def __str__(self):
        return self.name  # Return the name as the string representation
```

### 2. Create CarModel Django Model

Create a car model Django model `class CarModel(models.Model)`:
* Many-to-one relationship to `CarMake` model (One car make can have many car models, using a ForeignKey field)
* Dealer Id (IntegerField) refers to a dealer created in Cloudant database
* Name
* Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, and Wagon)
* Year (DateField)
* Any other fields you would like to include in a car model
* A `__str__` method to print the car make and car model object

**Sample Implementation:**

```python
class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)  # Many-to-One relationship
    name = models.CharField(max_length=100)
    CAR_TYPES = [
        ('SEDAN', 'Sedan'),
        ('SUV', 'SUV'),
        ('WAGON', 'Wagon'),
        # Add more choices as required
    ]
    type = models.CharField(max_length=10, choices=CAR_TYPES, default='SUV')
    year = models.IntegerField(default=2023,
        validators=[
            MaxValueValidator(2023),
            MinValueValidator(2015)
        ])
    # Other fields as needed
    
    def __str__(self):
        return self.name  # Return the name as the string representation
```

### 3. Register Models with Admin Site

You need to register the `CarMake` and `CarModel` on the admin site so you can conveniently manage their content (i.e., perform CRUD operations).

**Sample Code:**

```python
from django.contrib import admin
from .models import CarMake, CarModel

# Registering models with their respective admins
admin.site.register(CarMake)
admin.site.register(CarModel)
```

### 4. Run Migrations

Run migrations for the models:

```bash
python3 manage.py makemigrations
python3 manage.py migrate --run-syncdb
```

> **Note:** The `--run-syncdb` allows creating tables for apps without migrations.

## Steps to Register CarMake and CarModel Models with Admin Site

### 1. Create Superuser Access
First, you must have superuser access on the admin site (if not created before).
Please use `root` as the user name and `root` as the password for your reviewer to log in to your app.

### 2. Build Frontend
Open a new terminal and build your client by running the following commands:

```bash
cd /home/project/xrwvm-fullstack_developer_capstone/server/frontend
npm install
npm run build
```

### 3. Start Django Server
Start the server from the terminal where django application was running if it is not already running:

```bash
python3 manage.py runserver
```

### 4. Access Admin Site
Click the button below to launch the admin page to login with the root credentials.

**Django Admin**

> **Troubleshooting:** If you get an error, it is caused because the URL has changed. Copy the new application URL and make necessary changes in `server/djangoproj/settings.py`.

## Screenshots for Peer Review

### Required Screenshots:
1. After you log in to the admin site, please take a screenshot and name it as `admin_login.jpg` or `admin_login.png` for peer review.
2. You may want to log out as the admin user. You will be redirected to the admin login page again. Take a screenshot and name it `admin_logout.jpg` or `admin_logout.png`.

## Implementation Steps

### 5. Update Views
Open `djangoapp/views.py`, import CarMake and CarModel after the other import statements:

```python
from .models import CarMake, CarModel
```

Add a method to get the list of cars:

```python
def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if(count == 0):
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels":cars})
```

### 6. Update URLs
Open `server/djangoapp/urls.py` and add the path for `get_cars`:

```python
path(route='get_cars', view=views.get_cars, name ='getcars'),
```

### 7. Populate Data
Open `server/djangoapp/populate.py` and paste the following code to populate data in your database. The data is populated when the first call is made to `get_cars`, if the CarModel is empty. If you wish to add data manually, skip this step.

## Summary

By completing these steps, you will have successfully:
- Created CarMake and CarModel Django models
- Registered them with the Django admin site
- Set up views to retrieve car data
- Configured URL routing for the new endpoints
- Prepared data population functionality


# Create Django Views to Get Dealers

## 1. Update the `get_dealerships` view method

Update the `get_dealerships` view method in `djangoapp/views.py` with the following code. It will use the `get_request` you implemented in the `restapis.py` passing the `/fetchDealers` endpoint.

```python
# Update the `get_dealerships` render list of dealerships all by default, particular state if state is passed
def get_dealerships(request, state="All"):
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/"+state
    dealerships = get_request(endpoint)
    return JsonResponse({"status":200,"dealers":dealerships})
```

## 2. Configure the route for `get_dealerships` view method

Configure the route for `get_dealerships` view method in `url.py`:

```python
path(route='get_dealers', view=views.get_dealerships, name='get_dealers'),
path(route='get_dealers/<str:state>', view=views.get_dealerships, name='get_dealers_by_state'),
```

## 3. Create a `get_dealer_details` method

Create a `get_dealer_details` method which takes the dealer_id as a parameter in `views.py` and add a mapping urls.py. It will use the `get_request` you implemented in the `restapis.py` passing the `/fetchDealer/<dealer id>` endpoint.

### Add the following to views.py

```python
def get_dealer_details(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchDealer/"+str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status":200,"dealer":dealership})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})
```

### Add the following to urls.py

```python
path(route='dealer/<int:dealer_id>', view=views.get_dealer_details, name='dealer_details'),
```

## 4. Create `get_dealer_reviews` method

Create `get_dealer_reviews` method which takes the dealer_id as a parameter in `views.py` and add a mapping urls.py. It will use the `get_request` you implemented in the `restapis.py` passing the `/fetchReviews/dealer/<dealer id>` endpoint. It will also call `analyze_review_sentiments` in `restapis.py` to consume the microservice and determine the sentiment of each of the reviews and set the value in the `review_detail` dictionary which is returned as a JsonResponse.

The value of `sentiment` attribute will be determined by sentiment analysis microservice. It could be `positive`, `neutral`, or `negative`.

### Add the following to views.py

```python
def get_dealer_reviews(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchReviews/dealer/"+str(dealer_id)
        reviews = get_request(endpoint)
        
        # Analyze sentiment for each review
        for review_detail in reviews:
            # Call sentiment analysis microservice
            sentiment = analyze_review_sentiments(review_detail['review'])
            review_detail['sentiment'] = sentiment
            
        return JsonResponse({"status":200,"reviews":reviews})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})
```

### Add the following to urls.py

```python
path(route='reviews/dealer/<int:dealer_id>', view=views.get_dealer_reviews, name='dealer_reviews'),
```

## Summary

These Django views provide a complete API for:

- **Getting all dealerships** or filtering by state
- **Getting specific dealer details** by dealer ID
- **Getting dealer reviews** with sentiment analysis

Each view returns properly formatted JSON responses with appropriate status codes and error handling.
