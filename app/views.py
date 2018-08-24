from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.http import HttpResponse
from .forms import resume_upload
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Jobs, Company, Cv, Education, Experience, Award
# from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.core import serializers
from json import loads as json_loads
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model


User = get_user_model()
# User = settings.AUTH_USER_MODEL

def index(request):
    context = {
        'title': 'Find a Job | OdamaCareer',
    }

    return render(request,"index.html",context)


def jobs(request):
    query = request.GET.get('keywords')
    location = request.GET.get('location')
    order = request.GET.get('order_by')
    per_page = request.GET.get('per_page')
    page_num = request.GET.get('page',1)

    if query:
        results = Jobs.objects.filter(title__icontains=query)
        title = query + " Jobs"
	    
        if location:
            results = Jobs.objects.filter(office__company__city__icontains=location)
            title = query + " Jobs " + "in " + location
	        
    if location:
        title = "All jobs in " + location
        results = Jobs.objects.filter(title__icontains=query, office__company__city__icontains=location)

    elif not query and not location:
        title = "Job results"
        results = Jobs.objects.all()

    if order:
        results = results.order_by(order)
    else:
        order = "created"

    if per_page:
        paginator = Paginator(results, per_page)
    else:
        per_page = 9
        paginator = Paginator(results, per_page)

    results = paginator.get_page(page_num)


    context = {
        'title': title,
        'items': results,
        'location': location,
        'query': query,
        'order':order,
        'per_page':per_page,
        'page_num':page_num,
    }
    
    return render(request, 'jobs.html', context)


def browse(request):
    company = Company.objects.all()

    context = {
        'company':company,
    }
    return render(request, 'browse.html', context)


def browse_jobs(request):
    keyword = request.GET.get('keyword', None)
    company = Company.objects.filter(title__icontains=keyword)
    data = serializers.serialize("json", company, fields=('title','country','city','logo'))
    return JsonResponse({'data':json_loads(data),})


def job_at_company(request, slug):
    company = Company.objects.get(slug=slug)
    results = Jobs.objects.filter(office__company__slug=slug)
    title = 'Jobs at ' + str(company)
    context = {
        'title':title,
        'company':company,
        'items':results
    }

    return render(request, 'jobs.html',context)


def job_detail(request,slug):
    jobs = Jobs.objects.get(slug=slug)
    title = str(jobs) + ' | OdamaCareer'
    context = {
        'title':title,
        'jobs':jobs,
    }
    return render(request, 'job_detail.html', context)


def company_detail(request,slug):
    company = Company.objects.get(slug=slug)
    jobs = Jobs.objects.filter(office__company__slug=slug)

    context = {
        'company':company,
        'jobs':jobs,
    }
    return render(request, 'company_detail.html', context)


def profile(request):
    user = request.user
    profile = User.objects.get(userprofile__user=user)
    education = Education.objects.filter(user=user).order_by('-year_to')
    cv = Cv.objects.get(user__userprofile__user=user)
    experience = Experience.objects.filter(user=user).order_by("-job_to")
    awards = Award.objects.filter(user=user).order_by("-year")
    context = {
        'profile':profile,
        'education':education,
        'cv':cv,
        'experience':experience,
        'awards':awards,
    }
    return render(request, 'profile.html',context)


def resume(request):
    user = request.user
    profile = User.objects.get(userprofile__user=user)
    education = Education.objects.filter(user=user).order_by('-year_to')
    experience = Experience.objects.filter(user=user).order_by("-job_to")
    awards = Award.objects.filter(user=user).order_by("-year")

    context = {
        'title':'Resumes',
        'education':education,
        'experience':experience,
        'awards':awards,
    }
    return render(request, 'resume.html', context)


def resume_view(request, slug):
    resumes = Cv.objects.filter(slug=slug)

    context = {
        'title':'Resumes',
        'resumes':resumes,
    }
    return render(request, 'resumes.html', context)


def upload_resume(request):
    if request.method == 'POST':
        form = resume_upload(request.POST, request.FILES)
        if form.is_valid():
            cv_form = form.save()
            cv_form.user = request.user
            form.save(commit=True)
            return redirect('/resumes')
        else:
            messages.error(request, "Oops! That didn't work. Please try again")
    else:
        form = resume_upload()

    return render(request, 'upload_resume.html',{'form': form, 'title': 'Upload a Resume'})


def how_it_works(request):
    return render(request, 'others/how_it_works.html')
