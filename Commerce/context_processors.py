from .models import Notifications
def notification_processor(request):
    if request.user.is_authenticated:
            active_notif = Notifications.objects.filter(noti_user=request.user.profile).all()
    return {
          'notifs': active_notif
    }