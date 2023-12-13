from django.contrib import admin
from .models import Advertiser, Ad, Button, AdObject

# Register your models here.
admin.site.register(Advertiser)
admin.site.register(Ad)
admin.site.register(Button)
admin.site.register(AdObject)
