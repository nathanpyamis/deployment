def user_role_context(request):
    is_officer = False
    if request.user.is_authenticated:
        is_officer = request.user.groups.filter(name='Scholarship Officers').exists()
    return {
        'is_officer': is_officer
    }
