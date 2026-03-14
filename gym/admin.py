from django.contrib import admin
from gym.models.gym_parameters import GymParameters
from .models.gym_tenant import GymTenant, Domain


class GymParametersInline(admin.StackedInline):
    model = GymParameters
    extra = 0


class GymTenantAdmin(admin.ModelAdmin):
    inlines = [GymParametersInline]


admin.site.register(GymTenant, GymTenantAdmin)
admin.site.register(Domain)
admin.site.register(GymParameters)
