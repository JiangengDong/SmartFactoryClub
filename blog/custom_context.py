from django.conf import settings
from .models import Category

def customContext(request):
    return {'site_name': settings.SITE_NAME,
            'categories': Category.objects.all()}