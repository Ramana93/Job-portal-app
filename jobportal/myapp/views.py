from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from . models import Job, Application, Profile 
from django.core.paginator import Paginator


from django.core.paginator import Paginator

def home(request):
    jobs = Job.objects.all().order_by('-id')

    # FILTERS
    title = request.GET.get('title')
    location = request.GET.get('location')
    experience = request.GET.get('experience')
    salary = request.GET.get('salary')

    if title:
        jobs = jobs.filter(title__icontains=title)

    if location:
        jobs = jobs.filter(location__icontains=location)

    if experience:
        jobs = jobs.filter(experience__icontains=experience)

    if salary:
        jobs = jobs.filter(salary__icontains=salary)

    # Attach application status for seeker
    if request.user.is_authenticated and request.user.profile.role == 'seeker':
        applications = Application.objects.filter(applicant=request.user)
        apps_dict = {app.job_id: app for app in applications}

        for job in jobs:
            job.user_application = apps_dict.get(job.id)

    # PAGINATION
    paginator = Paginator(jobs, 3)
    page_number = request.GET.get("page")
    jobs_page = paginator.get_page(page_number)

    return render(request, "home.html", {
        "jobs": jobs_page
    })

def register_view(request):

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists! Please try another.")
            return redirect('register')

        # Create user
        user = User.objects.create_user(username=username, password=password)

        # Create profile with role
        Profile.objects.create(
            user=user,
            role=role
        )

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
    if request.user.profile.role != "recruiter":
        messages.error(request, "Only Recruiters can post jobs.")
        return redirect("home")
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
    if request.user.profile.role != "seeker":
        messages.error(request, "Only Job Seekers can apply for jobs.")
        return redirect("home")
    
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
def delete_job(request, pk):
    if request.user.profile.role != "recruiter":
        messages.error(request, "Access Denied! Only recruiters can delete jobs.")
        return redirect("home")

    job = Job.objects.get(pk=pk)
    job.delete()

    messages.success(request, "Job deleted successfully!")
    return redirect("home")

@login_required
def edit_job(request, pk):
    if request.user.profile.role != "recruiter":
        messages.error(request, "Access Denied! Only recruiters can update jobs.")
        return redirect("home")

    job = Job.objects.get(pk=pk)

    if request.method == "POST":
        job.title = request.POST.get("title")
        job.company = request.POST.get("company")
        job.location = request.POST.get("location")
        job.salary = request.POST.get("salary")
        job.experience = request.POST.get("experience")
        job.description = request.POST.get("description")

        job.save()

        messages.success(request, "Job updated successfully!")
        return redirect("home")

    return render(request, "edit_job.html", {"job": job})

def update_status(request, pk, status):

    application = Application.objects.get(pk=pk)
    application.status = status
    application.save()

    return redirect('view_applicants', pk=application.job.pk)

@login_required
def view_applicants(request, pk):
    job = get_object_or_404(Job, pk=pk)

    if request.user.profile.role != "recruiter":
        messages.error(request, "Access Denied!")
        return redirect("home")

    applicants = job.application_set.all()  # all applicants for this job

    # Handle status update
    if request.method == "POST":
        app_id = request.POST.get("application_id")
        new_status = request.POST.get("status")
        application = get_object_or_404(Application, pk=app_id)
        if new_status in ['waiting', 'selected', 'rejected']:
            application.status = new_status
            application.save()
            messages.success(request, f"{application.name}'s status updated to {new_status.capitalize()}")
        return redirect('view_applicants', pk=pk)

    return render(request, "view_applicants.html", {"job": job, "applicants": applicants})