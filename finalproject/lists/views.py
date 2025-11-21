# lists/views.py
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

from .models import Comment, JobListing, User

# Create your views here.
def index(request):
    listings = JobListing.objects.filter(percentage__lt=100).order_by("deadline")
    message = None
    if not listings:
        message = 'There are no listings yet.'
    return render(request, 'index.html', {
        "listings": listings,
        "now": timedelta(hours=6),
        "message": message,
        "title": 'Tasks'
    })

# The new, combined view replaces show_listing and comment
def listing_detail_view(request, listing_id):
    listing = get_object_or_404(JobListing, my_id=listing_id)

    if request.method == "POST":
        # Handle comment submission logic here
        if request.user.is_authenticated:
            # Using .get() is safer than request.POST['key']
            title = request.POST.get('title')
            content = request.POST.get('description')

            if title and content:
                Comment.objects.create(
                    listing=listing,
                    author=request.user, # request.user is already the instance
                    title=title,
                    content=content
                )
        # Always redirect back to the detail page after a POST request
        return redirect('listing_detail', listing_id=listing_id)

    else: # This handles the initial GET request to view the page
        comments = Comment.objects.filter(listing=listing).order_by('-timestamp')
        return render(request, 'listing.html', {
            "listing": listing,
            "now": timezone.now(),
            "comments": comments
        })

@login_required(login_url='/login')
def create(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        deadline_str = request.POST['deadline']
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
            # Make the naive datetime aware using the configured timezone (UTC by default)
            deadline = timezone.make_aware(deadline)
        except ValueError:
            return render(request, 'create.html', {"message": "Invalid deadline format"})

        if deadline <= timezone.now():
            return render(request, 'create.html', {"message": "Deadline must be in the future"})

        JobListing.objects.create(title=title, description=description, deadline=deadline, percentage=0)
        return redirect('index')
    return render(request, 'create.html')


@login_required(login_url='/login')
def signed_up(request):
    listings = JobListing.objects.filter(signed_up=request.user).order_by('deadline')
    message = None
    if not listings:
        message = 'You have signed up for no Jobs yet.'
    return render(request, 'index.html', {
        "listings": listings,
        "now": timedelta(hours=6),
        "message": message,
        "title": 'Signed Up'
    })

def completed(request):
    listings = JobListing.objects.filter(percentage=100).order_by('deadline')
    message = None
    if not listings:
        message = 'You have completed no tasks yet'
    return render(request, 'index.html', {
        "listings": listings,
        "now": timedelta(hours=6),
        "message": message,
        "title": 'Completed'
    })

@login_required(login_url='/login')
def add_to_listing(request, listing_id):
    listing = get_object_or_404(JobListing, my_id=listing_id)
    listing.signed_up.add(request.user)
    # Use the new unified view name for redirection
    return redirect('listing_detail', listing_id=listing_id)

@login_required(login_url='/login')
def remove_from_listing(request, listing_id):
    listing = get_object_or_404(JobListing, my_id=listing_id)
    listing.signed_up.remove(request.user)
    # Use the new unified view name for redirection
    return redirect('listing_detail', listing_id=listing_id)

@login_required(login_url='/login')
@require_POST
def update_progress(request, listing_id):
    try:
        # Use get_object_or_404 for robustness
        listing = get_object_or_404(JobListing, my_id=listing_id)

        json_data_str = request.body.decode('utf-8')
        data = json.loads(json_data_str)
        progress_value = int(data.get('progress_value', 0)) # Ensure it's an integer

        # Validate the range (e.g., between 0 and 100)
        if 0 <= progress_value <= 100:
            listing.percentage = progress_value
            listing.save()
            # Return success response
            return JsonResponse({'percentage': listing.percentage, 'message': False})
        else:
            # Return an error message for invalid range
            return JsonResponse({'percentage': listing.percentage, 'message': True, 'error_msg': 'Invalid progress value (must be 0-100)'}, status=400) # Use HTTP 400 Bad Request

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'Invalid number format'}, status=400)
    except Exception as e:
        # Generic error handler to prevent 500 HTML response
        return JsonResponse({'error': str(e)}, status=500)



def login_view(request):
    if request.method == "POST":
        # ... (login logic remains the same) ...
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        # ... (register logic remains the same) ...
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "register.html", {
                "message": "Username already taken."
            })

        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "register.html")
