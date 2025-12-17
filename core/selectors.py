

def get_dashboard_info(request):
    return {
        "gym_name": request.tenant.name,
        "coach_name": request.user.coach.name
    }
