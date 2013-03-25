from .models import Subscription

def sub_list(request):
    if not request.user.is_authenticated():
        return ()
    return {
        'sub_list': Subscription.objects.filter(user=request.user).select_related("feed")
    }
