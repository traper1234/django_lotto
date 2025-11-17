from django.contrib import admin
from .models import Ticket, Draw


@admin.register(Draw)
class DrawAdmin(admin.ModelAdmin):
    list_display = ('id', 'numbers')
    list_editable = ('numbers',)
    ordering = ('-id',)
    fields = ('numbers',)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'numbers', 'is_auto', 'created_at')
    list_filter = ('is_auto', 'created_at')
    search_fields = ('user__username', 'numbers')
    readonly_fields = ('created_at',)