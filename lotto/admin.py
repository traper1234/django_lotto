from django.contrib import admin
from django.core.exceptions import PermissionDenied
from .models import Ticket, Draw


@admin.register(Draw)
class DrawAdmin(admin.ModelAdmin):
    list_display = ('id', 'numbers', 'bonus_number', 'drawn_at', 'is_active')
    list_filter = ('is_active', 'drawn_at')
    ordering = ('-drawn_at',)
    fields = ('numbers', 'bonus_number', 'is_active')
    readonly_fields = ('drawn_at',)
    
    def has_add_permission(self, request):
        """superuser만 당첨번호 추가 가능"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """superuser만 당첨번호 수정 가능"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """superuser만 당첨번호 삭제 가능"""
        return request.user.is_superuser
    
    def save_model(self, request, obj, form, change):
        """일반 staff 사용자가 저장하려고 하면 차단"""
        if not request.user.is_superuser:
            raise PermissionDenied("당첨번호 등록/수정은 관리자(superuser)만 가능합니다.")
        super().save_model(request, obj, form, change)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'numbers', 'is_auto', 'winning_grade', 'draw', 'created_at')
    list_filter = ('is_auto', 'winning_grade', 'created_at', 'draw')
    search_fields = ('user__username', 'numbers')
    readonly_fields = ('created_at', 'winning_grade', 'draw', 'user', 'numbers', 'is_auto')
    ordering = ('-created_at',)
    
    def has_add_permission(self, request):
        """티켓은 admin에서 추가 불가 (사용자가 직접 구매)"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """티켓은 admin에서 수정 불가 (읽기 전용)"""
        return request.user.is_staff
    
    def has_delete_permission(self, request, obj=None):
        """superuser만 티켓 삭제 가능"""
        return request.user.is_superuser