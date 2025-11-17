from django.db import models
from django.contrib.auth.models import User

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    numbers = models.CharField(max_length=100)  # "1,2,3,4,5,6" 이런 식
    is_auto = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '로또 티켓'
        verbose_name_plural = '로또 티켓'

    def __str__(self):
        return f"티켓 {self.id} - {self.user.username}"


class Draw(models.Model):
    numbers = models.CharField(max_length=100, verbose_name='당첨 번호')  # 당첨 번호 "1,2,3,4,5,6"

    class Meta:
        verbose_name = '로또 당첨번호'
        verbose_name_plural = '로또 당첨번호'

    def __str__(self):
        return f"당첨번호: {self.numbers}"
