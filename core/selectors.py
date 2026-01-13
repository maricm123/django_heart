

def get_dashboard_info(request):
    active_members = request.tenant.cilent
    return {
        "gym_name": request.tenant.name,
        "coach_name": request.user.coach.name,
        "active_members": active_members
    }
