from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from . models import Job, Application


def home(request):
    jobs = Job.objects.all()
    return render(request, 'home.html', {'jobs': jobs})



def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists! Please try another.")
            return redirect('register')

        # Create new user
        User.objects.create_user(username=username, password=password)
        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')

    return render(request, 'register.html')


def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, 'login.html')


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')


@login_required
def post_job(request):
    if request.method == "POST":
        title = request.POST['title']
        company = request.POST['company']
        location = request.POST['location']
        salary = request.POST['salary']
        experience = request.POST['experience']
        description = request.POST['description']

        Job.objects.create(
            title=title,
            company=company,
            location=location,
            salary=salary,
            experience=experience,
            description=description,
            posted_by=request.user
        )

        return redirect('home')

    return render(request, 'post_job.html')


@login_required
def apply_job(request,pk):
    job = Job.objects.get(pk=pk)
    job = get_object_or_404(Job, id=pk)

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        cover_letter = request.POST.get('cover_letter')
        resume = request.FILES.get('resume')

        Application.objects.create(
            job=job,
            applicant=request.user,
            name=name,
            email=email,
            phone=phone,
            cover_letter=cover_letter,
            resume=resume
        )
        messages.success(request, "You have successfully applied for this job!")
        return redirect('home')

    return render(request, 'apply_job.html', {'job': job})

@login_required
def delete_job(request, job_pk):
    job = Job.objects.get(pk=job_pk)
    job.delete()
    messages.success(request, "Job deleted successfully!")
    return redirect('home')

@login_required
def edit_job(request, pk):
    job = get_object_or_404(Job, pk=pk)

    if request.method == "POST":
        job.title = request.POST.get('title')
        job.company = request.POST.get('company')
        job.location = request.POST.get('location')
        job.salary = request.POST.get('salary')
        job.experience = request.POST.get('experience')
        job.description = request.POST.get('description')
        job.save()

        messages.success(request, "Job updated successfully!")
        return redirect('home')

    return render(request, 'edit_job.html', {'job': job})