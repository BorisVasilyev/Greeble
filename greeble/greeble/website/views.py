from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect

from .forms import SignUpForm


def landing(request):
	template = loader.get_template('website/landing.html')

	context = {
	}

	return HttpResponse(template.render(context, request))


def signup(request):
	form = SignUpForm(request.POST)

	if form.is_valid():
		form.save()

		username = form.cleaned_data.get('username')
		password = form.cleaned_data.get('password1')
		user = authenticate(username=username, password=password)

		login(request, user)

		return redirect('/lms/login')
	else:
		form = SignUpForm()

	return render(request, 'website/signup.html', {'form': form})
