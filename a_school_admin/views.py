from django.shortcuts import render
from common.models import UserProfile, CustomUser
from django.contrib.auth.decorators import login_required


@login_required
def school_admin_dashboard(request):
    # user = UserProfile.objects.get(user=request.user)
    names = list(CustomUser.objects.values_list('first_name', flat=True))
    context = {
        # "user_pic_url8": user.user_pic.url,
        # "username8": user.username,
        "names": names,
    }
    return render(request, "a_school_admin/dashboard.html", context)


def user_search(request):
    names = list(CustomUser.objects.values_list('first_name', flat=True))
    return render(request, 'a_school_admin/example.html', {'names': names})