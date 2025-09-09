from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib import messages

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name,
                    "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels": cars})


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


def logout_request(request):
    logout(request)  # Terminate user session
    data = {"userName": ""}  # Return empty username
    return JsonResponse(data)


@csrf_exempt
def registration(request):

    # Load JSON data from the request body
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except User.DoesNotExist:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(
            username=username, first_name=first_name,
            last_name=last_name, password=password, email=email)
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(data)
    else:
        data = {"userName": username, "error": "Already Registered"}
        return JsonResponse(data)


def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state
    dealerships = get_request(endpoint)
    context = {'dealers': dealerships}
    return render(request, 'dealers_list.html', context)


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


def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchDealer/" + str(dealer_id)
        dealership = get_request(endpoint)
        context = {'dealer': dealership}
        return render(request, 'dealer_details.html', context)
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


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

            response = requests.post(
                f'{backend_url}/insert_review',
                data=json.dumps(review_data),
                headers={'Content-Type': 'application/json'})

            if response.status_code == 200:
                messages.success(
                    request,
                    f'Thank you {name}! Review submitted successfully.')
            else:
                messages.error(
                    request,
                    'Error submitting review. Please try again.')
        except Exception:
            messages.error(
                request, 'Error submitting review. Please try again.')

        context = {'dealer_id': dealer_id}
        return render(request, 'post_review.html', context)
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


def add_review(request):
    from .restapis import post_review
    if not request.user.is_anonymous:
        data = json.loads(request.body)
        try:
            post_review(data)
            return JsonResponse({"status": 200})
        except Exception:
            return JsonResponse(
                {"status": 401, "message": "Error in posting review"})
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})
