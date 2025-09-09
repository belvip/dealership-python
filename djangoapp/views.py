
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

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

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        # Get username and password from request.POST dictionary
        data = json.loads(request.body)
        username = data['userName']
        password = data['password']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        data = {"userName": username}
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "POST method required"})

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)  # Terminate user session
    data = {"userName": ""}  # Return empty username
    return JsonResponse(data)

# Create a `registration` view to handle sign up request
# @csrf_exempt
# def registration(request):
# ...

@csrf_exempt
def registration(request):
    context = {}

    # Load JSON data from the request body
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    email_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=password, email=email)
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName":username,"status":"Authenticated"}
        return JsonResponse(data)
    else :
        data = {"userName":username,"error":"Already Registered"}
        return JsonResponse(data)

# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
# def get_dealerships(request):
# ...

def get_dealerships(request, state="All"):
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/"+state
    dealerships = get_request(endpoint)
    context = {'dealers': dealerships}
    return render(request, 'dealers_list.html', context)

# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchReviews/dealer/" + str(dealer_id)
        reviews = get_request(endpoint)
        if reviews is None:
            reviews = []
        else:
            for review_detail in reviews:
                response = analyze_review_sentiments(review_detail['review'])
                if response and 'sentiment' in response:
                    review_detail['sentiment'] = response['sentiment']
                else:
                    review_detail['sentiment'] = 'neutral'
        context = {'reviews': reviews, 'dealer_id': dealer_id}
        return render(request, 'dealer_reviews.html', context)
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})

# Create a `get_dealer_details` view to render the dealer details
# def get_dealer_details(request, dealer_id):
# ...

def get_dealer_details(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchDealer/"+str(dealer_id)
        dealership = get_request(endpoint)
        context = {'dealer': dealership}
        return render(request, 'dealer_details.html', context)
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

# Create a `add_review` view to submit a review
def post_review(request, dealer_id):
    if request.method == 'GET':
        context = {'dealer_id': dealer_id}
        return render(request, 'post_review.html', context)
    elif request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        review_text = request.POST.get('review')
        purchase = request.POST.get('purchase') == 'on'
        car_make = request.POST.get('car_make', '')
        car_model = request.POST.get('car_model', '')
        car_year = request.POST.get('car_year', '')
        purchase_date = request.POST.get('purchase_date', '')
        
        # Create review data
        review_data = {
            'name': name,
            'dealership': dealer_id,
            'review': review_text,
            'purchase': purchase,
            'car_make': car_make,
            'car_model': car_model,
            'car_year': car_year,
            'purchase_date': purchase_date
        }
        
        # Submit review to API
        try:
            import requests
            import json
            from .restapis import backend_url
            
            response = requests.post(f'{backend_url}/insert_review', 
                                   data=json.dumps(review_data),
                                   headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                messages.success(request, f'Thank you {name}! Your review has been submitted successfully.')
            else:
                messages.error(request, 'There was an error submitting your review. Please try again.')
        except Exception as e:
            messages.error(request, 'There was an error submitting your review. Please try again.')
        
        context = {'dealer_id': dealer_id}
        return render(request, 'post_review.html', context)
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})

def add_review(request):
    if(request.user.is_anonymous == False):
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status":200})
        except:
            return JsonResponse({"status":401,"message":"Error in posting review"})
    else:
        return JsonResponse({"status":403,"message":"Unauthorized"})
