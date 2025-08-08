from django.contrib import admin
from .models.user import User
from .models.client import Client
from .models.coach import Coach
from .models.gym_manager import GymManager

admin.site.register(GymManager)
admin.site.register(Client)
admin.site.register(Coach)
admin.site.register(User)
