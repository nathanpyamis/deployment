from django.shortcuts import redirect
from functools import wraps

def require_password_setup(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.has_usable_password():
            return redirect('set_password')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
