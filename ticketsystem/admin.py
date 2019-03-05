from django.contrib import admin

# Register your models here.

from .models import Issue
from .models import State
from .models import ProblemClass
from .models import HistoryElement
from .models import Mail
from .models import Address
from .models import DailyNotificationSubscriber
from .models import Attachment

admin.site.register(State)

admin.site.register(Issue)
admin.site.register(HistoryElement)
admin.site.register(Mail)
admin.site.register(Address)
admin.site.register(Attachment)
admin.site.register(DailyNotificationSubscriber)
