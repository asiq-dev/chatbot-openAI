from django.contrib import admin
from django.contrib.admin import site
from .models import Customer, Message

# Register your models here.
admin.site.register(Customer)
admin.site.register(Message)