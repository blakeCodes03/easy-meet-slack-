from django.urls import path, include
from api.views import BotSettings
from api.views import handle_slack_event

urlpatterns = [
    # path('', BotSettings.as_view()),
     path('', handle_slack_event, name='slack_event')
]