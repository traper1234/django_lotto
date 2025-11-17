from django import forms
from .models import Ticket

class LottoBuyForm(forms.ModelForm):

    numbers = forms.CharField(
        required=False,
        label='번호 (쉼표로 구분, 예: 1,5,12,20,33,42)',
        widget=forms.TextInput(attrs={
            'placeholder': '1,5,12,20,33,42',
        })
    )

    is_auto = forms.BooleanField(
        required=False,
        label='자동 구매',
        initial=True,
    )

    class Meta:
        model = Ticket
        fields = ['numbers', 'is_auto']

    def clean(self):
        cleaned_data = super().clean()
        numbers = cleaned_data.get('numbers')
        is_auto = cleaned_data.get('is_auto')

        if is_auto:
            cleaned_data['numbers'] = ""
            return cleaned_data

        if not numbers:
            raise forms.ValidationError("수동 구매 시 번호를 반드시 입력해야 합니다.")

        nums = numbers.split(',')
        if len(nums) != 6:
            raise forms.ValidationError("번호는 반드시 6개를 입력해야 합니다.")

        try:
            nums = [int(n.strip()) for n in nums]
        except:
            raise forms.ValidationError("번호는 숫자만 입력해야 합니다.")

        for n in nums:
            if not (1 <= n <= 45):
                raise forms.ValidationError("로또 번호는 1~45 사이여야 합니다.")

        if len(set(nums)) != 6:
            raise forms.ValidationError("번호는 중복 없이 6개를 입력해야 합니다.")

        cleaned_data['numbers'] = ",".join([str(n) for n in nums])
        return cleaned_data