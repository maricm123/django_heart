from django.contrib import admin
from .models.gym_tenant import GymTenant, Domain

admin.site.register(GymTenant)
admin.site.register(Domain)
