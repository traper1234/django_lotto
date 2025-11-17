from django.db import models
from django.contrib.auth.models import User

class Ticket(models.Model):
    WINNING_GRADE_CHOICES = [
        (0, '낙첨'),
        (1, '1등'),
        (2, '2등'),
        (3, '3등'),
        (4, '4등'),
        (5, '5등'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    numbers = models.CharField(max_length=100)  # "1,2,3,4,5,6" 이런 식
    is_auto = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    winning_grade = models.IntegerField(default=0, choices=WINNING_GRADE_CHOICES, verbose_name='당첨 등급')
    draw = models.ForeignKey('Draw', on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')

    class Meta:
        verbose_name = '로또 티켓'
        verbose_name_plural = '로또 티켓'
        ordering = ['-created_at']

    def __str__(self):
        return f"티켓 {self.id} - {self.user.username}"

    def get_numbers_list(self):
        """번호 문자열을 리스트로 변환"""
        return [int(n.strip()) for n in self.numbers.split(',')]


class Draw(models.Model):
    numbers = models.CharField(max_length=100, verbose_name='당첨 번호')  # 당첨 번호 "1,2,3,4,5,6"
    bonus_number = models.IntegerField(null=True, blank=True, verbose_name='보너스 번호')
    drawn_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='추첨일시')
    is_active = models.BooleanField(default=True, verbose_name='활성화')

    class Meta:
        verbose_name = '로또 당첨번호'
        verbose_name_plural = '로또 당첨번호'
        ordering = ['-drawn_at']

    def __str__(self):
        if self.drawn_at:
            return f"당첨번호: {self.numbers} (추첨일: {self.drawn_at.strftime('%Y-%m-%d %H:%M')})"
        return f"당첨번호: {self.numbers}"

    def get_numbers_list(self):
        """당첨번호 문자열을 리스트로 변환"""
        return [int(n.strip()) for n in self.numbers.split(',')]
