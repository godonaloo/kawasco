from django.urls import path
from .views import (
    signup,
    login,
    applications,
    complaints,
    home,
    dashboard,
    count_pending_applications,
    count_completed_applications,
    count_in_progress_applications
)

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name="signup"),
    path('login/', login, name="login"),
    path('dashboard/', dashboard, name="dashboard"),
    path('applications/', applications, name="applications"),
    path('complaints/', complaints, name='complaints'),
    path('pending-applications/', count_pending_applications, name="pending-applications"),
    path('in-progress-applications/', count_in_progress_applications, name="in-progress-applications"),
    path('completed-applications/', count_completed_applications, name="completed-applications"),
]
