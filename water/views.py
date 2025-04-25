# Standard library imports
import json

# Third-party imports
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

# Local app imports
from .models import User, WaterInstallationApplication, Complaint

# Helper to fetch user by username
def get_user_by_username(username):
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None

def home(request):
    return render(request, 'home.html')

def dashboard(request):
    return render(request, 'dashboard.html')


@csrf_exempt
def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            username = data.get('username')
            email = data.get('email')
            password = data.get('password')

            if not all([username, email, password]):
                return HttpResponseBadRequest("Missing required fields.")

            if User.objects.filter(username=username).exists():
                return JsonResponse({"error": "Username already taken."}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "Email already in use."}, status=400)

            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password)
            )

            return JsonResponse({"message": "User created successfully!"}, status=201)

        except Exception as e:
            return HttpResponseBadRequest(str(e))

    return HttpResponseNotAllowed(['POST'])

@csrf_exempt
def login(request):
    # If it's a GET request, render the login page
    if request.method == 'GET':
        return render(request, 'login.html')  # Renders the login.html template
    
    # If it's a POST request, handle the login logic
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            username = data.get('username')
            password = data.get('password')

            if not all([username, password]):
                return HttpResponseBadRequest("Missing username or password.")

            user = User.objects.filter(username=username).first()  # Modify if you have a different user model
            if not user or not check_password(password, user.password):
                return JsonResponse({"error": "Invalid username or password."}, status=400)

            response_data = {
                "username": user.username
            }

            return JsonResponse({"message": "Login successful", "user": response_data}, status=200)

        except Exception as e:
            return HttpResponseBadRequest(str(e))

    return HttpResponseNotAllowed(['POST'])

@csrf_exempt
def applications(request):
    if request.method == 'GET':
        username = request.GET.get('username')
        if not username:
            return HttpResponseBadRequest("Missing username")

        user = get_user_by_username(username)
        if not user:
            return JsonResponse({"error": "User not found."}, status=404)

        applications = WaterInstallationApplication.objects.filter(user=user).order_by('-application_date')

        data = [
            {
                'id': a.id,
                'user': a.user.username,
                'phone_number': a.phone_number,
                'description': a.description,
                'application_date': a.application_date,
                'status': a.status
            } for a in applications
        ]
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')

            if not username:
                return HttpResponseBadRequest("Missing username")

            user = get_user_by_username(username)
            if not user:
                return JsonResponse({"error": "User not found."}, status=404)

            application = WaterInstallationApplication.objects.create(
                user=user,
                phone_number=data.get('phone_number', ''),
                description=data.get('description', ''),
            )

            return JsonResponse({'message': 'Application submitted successfully', 'id': application.id}, status=201)

        except Exception as e:
            return HttpResponseBadRequest(str(e))

    return HttpResponseNotAllowed(['GET', 'POST'])

@csrf_exempt
def count_pending_applications(request):
    # Get the username from the request
    username = request.GET.get('username')
    
    if not username:
        return HttpResponseBadRequest("Missing username")
    
    # Retrieve the user object using the username
    user = get_user_by_username(username)
    
    if not user:
        return JsonResponse({"error": "User not found."}, status=404)

    # Count the number of pending applications for the user
    pending_count = WaterInstallationApplication.objects.filter(user=user, status='Pending').count()

    # Return the count as a JSON response
    return JsonResponse({'pending_applications': pending_count}, status=200)

@csrf_exempt
def count_completed_applications(request):
    # Get the username from the request
    username = request.GET.get('username')
    
    if not username:
        return HttpResponseBadRequest("Missing username")
    
    # Retrieve the user object using the username
    user = get_user_by_username(username)
    
    if not user:
        return JsonResponse({"error": "User not found."}, status=404)

    # Count the number of completed applications for the user
    completed_count = WaterInstallationApplication.objects.filter(user=user, status='Completed').count()

    # Return the count as a JSON response
    return JsonResponse({'completed_applications': completed_count}, status=200)

@csrf_exempt
def count_in_progress_applications(request):
    # Get the username from the request
    username = request.GET.get('username')
    
    if not username:
        return HttpResponseBadRequest("Missing username")
    
    # Retrieve the user object using the username
    user = get_user_by_username(username)
    
    if not user:
        return JsonResponse({"error": "User not found."}, status=404)

    # Count the number of in progress applications for the user
    in_progress_count = WaterInstallationApplication.objects.filter(user=user, status='In Progress').count()

    # Return the count as a JSON response
    return JsonResponse({'in_progress_applications': in_progress_count}, status=200)

@csrf_exempt
def complaints(request):
    if request.method == 'GET':
        username = request.GET.get('username')
        if not username:
            return HttpResponseBadRequest("Missing username")

        user = get_user_by_username(username)
        if not user:
            return JsonResponse({"error": "User not found."}, status=404)

        complaints = Complaint.objects.filter(user=user).order_by('-submitted_at')

        data = [
            {
                'id': c.id,
                'application_id': c.application.id,
                'message': c.message,
                'response': c.response,
                'submitted_at': c.submitted_at,
                'responded_at': c.responded_at,
                'status': c.application.status
            }
            for c in complaints
        ]
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)

            username = data.get('username')
            app_id = data.get('application_id')

            if not all([username, app_id]):
                return HttpResponseBadRequest("Missing username or application ID.")

            user = get_user_by_username(username)
            if not user:
                return JsonResponse({"error": "User not found."}, status=404)

            try:
                application = WaterInstallationApplication.objects.get(id=app_id)
            except WaterInstallationApplication.DoesNotExist:
                return JsonResponse({"error": "Application not found."}, status=404)

            complaint = Complaint.objects.create(
                user=user,
                application=application,
                message=data.get('message', '')
            )

            return JsonResponse({'message': 'Complaint submitted successfully', 'id': complaint.id}, status=201)

        except Exception as e:
            return HttpResponseBadRequest(str(e))

    return HttpResponseNotAllowed(['GET', 'POST'])
