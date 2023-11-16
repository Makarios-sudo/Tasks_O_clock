from rest_framework.routers import DefaultRouter
from taskmangement.tasks.api.views import TeamViewSet

urlpatterns = []

app_name = "tasks"
router = DefaultRouter()
router.register(r"teams", TeamViewSet, basename="teams")


urlpatterns += router.urls
