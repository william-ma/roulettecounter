from django.contrib import admin

from .models import Session, NumberShown, BoardStat, NumberStat

# Register your models here.
admin.site.register(Session)
admin.site.register(NumberShown)
admin.site.register(NumberStat)
admin.site.register(BoardStat)
