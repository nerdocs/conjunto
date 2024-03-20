# Helper functions for authentication in menus
# use this for checks like
# class FooMenu(IMenuItem):
#     ...
#     check = is_authenticated


def is_staff(request):
    return request.user.is_staff


def is_authenticated(request):
    return request.user.is_authenticated


def is_anonymous(request):
    return request.user.is_anonymous
