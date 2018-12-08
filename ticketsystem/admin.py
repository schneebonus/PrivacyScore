from django.contrib import admin

# Register your models here.

from .models import Issue
from .models import State
from .models import ProblemClass
from .models import HistoryElement
from .models import Mail


admin.site.register(State)
admin.site.register(ProblemClass)

admin.site.register(Issue)
admin.site.register(HistoryElement)
admin.site.register(Mail)
