from django.http import HttpResponse
from django.template import loader


def landing(request):
	template = loader.get_template('website/landing.html')

	context = {
	}

	return HttpResponse(template.render(context, request))