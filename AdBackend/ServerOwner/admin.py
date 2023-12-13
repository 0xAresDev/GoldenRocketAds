from django.contrib import admin
from .models import Servers, AdvServerInfo, Channel


# Register your models here.
admin.site.register(Servers)
admin.site.register(AdvServerInfo)
admin.site.register(Channel)
