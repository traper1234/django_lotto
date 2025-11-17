from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Ticket, Draw
from .utils import calculate_winning_grade
import random


class TicketModelTest(TestCase):
    """Ticket 모델 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_ticket_creation(self):
        """티켓 생성 테스트"""
        ticket = Ticket.objects.create(
            user=self.user,
            numbers="1,2,3,4,5,6",
            is_auto=False
        )
        self.assertEqual(ticket.user, self.user)
        self.assertEqual(ticket.numbers, "1,2,3,4,5,6")
        self.assertFalse(ticket.is_auto)
        self.assertEqual(ticket.winning_grade, 0)  # 기본값 낙첨
    
    def test_get_numbers_list(self):
        """번호 리스트 변환 테스트"""
        ticket = Ticket.objects.create(
            user=self.user,
            numbers="1,2,3,4,5,6",
            is_auto=False
        )
        numbers = ticket.get_numbers_list()
        self.assertEqual(numbers, [1, 2, 3, 4, 5, 6])


class DrawModelTest(TestCase):
    """Draw 모델 테스트"""
    
    def test_draw_creation(self):
        """추첨 생성 테스트"""
        draw = Draw.objects.create(
            numbers="1,2,3,4,5,6",
            bonus_number=7,
            is_active=True
        )
        self.assertEqual(draw.numbers, "1,2,3,4,5,6")
        self.assertEqual(draw.bonus_number, 7)
        self.assertTrue(draw.is_active)
    
    def test_get_numbers_list(self):
        """당첨번호 리스트 변환 테스트"""
        draw = Draw.objects.create(
            numbers="1,2,3,4,5,6",
            bonus_number=7
        )
        numbers = draw.get_numbers_list()
        self.assertEqual(numbers, [1, 2, 3, 4, 5, 6])


class WinningGradeCalculationTest(TestCase):
    """당첨 등급 계산 테스트"""
    
    def test_1등_당첨(self):
        """1등: 6개 번호 일치"""
        ticket_nums = [1, 2, 3, 4, 5, 6]
        draw_nums = [1, 2, 3, 4, 5, 6]
        grade = calculate_winning_grade(ticket_nums, draw_nums)
        self.assertEqual(grade, 1)
    
    def test_2등_당첨(self):
        """2등: 5개 번호 일치 + 보너스 번호 일치"""
        ticket_nums = [1, 2, 3, 4, 5, 7]
        draw_nums = [1, 2, 3, 4, 5, 6]
        bonus = 7
        grade = calculate_winning_grade(ticket_nums, draw_nums, bonus)
        self.assertEqual(grade, 2)
    
    def test_3등_당첨(self):
        """3등: 5개 번호 일치"""
        ticket_nums = [1, 2, 3, 4, 5, 7]
        draw_nums = [1, 2, 3, 4, 5, 6]
        grade = calculate_winning_grade(ticket_nums, draw_nums)
        self.assertEqual(grade, 3)
    
    def test_4등_당첨(self):
        """4등: 4개 번호 일치"""
        ticket_nums = [1, 2, 3, 4, 7, 8]
        draw_nums = [1, 2, 3, 4, 5, 6]
        grade = calculate_winning_grade(ticket_nums, draw_nums)
        self.assertEqual(grade, 4)
    
    def test_5등_당첨(self):
        """5등: 3개 번호 일치"""
        ticket_nums = [1, 2, 3, 7, 8, 9]
        draw_nums = [1, 2, 3, 4, 5, 6]
        grade = calculate_winning_grade(ticket_nums, draw_nums)
        self.assertEqual(grade, 5)
    
    def test_낙첨(self):
        """낙첨: 2개 이하 일치"""
        ticket_nums = [1, 2, 7, 8, 9, 10]
        draw_nums = [1, 2, 3, 4, 5, 6]
        grade = calculate_winning_grade(ticket_nums, draw_nums)
        self.assertEqual(grade, 0)


class UserViewTest(TestCase):
    """사용자 뷰 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_home_page(self):
        """홈페이지 접근 테스트"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_signup_page(self):
        """회원가입 페이지 접근 테스트"""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
    
    def test_signup_success(self):
        """회원가입 성공 테스트"""
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # 리다이렉트
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_login_page(self):
        """로그인 페이지 접근 테스트"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_success(self):
        """로그인 성공 테스트"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # 리다이렉트
    
    def test_buy_ticket_requires_login(self):
        """티켓 구매는 로그인 필요"""
        response = self.client.get(reverse('buy_ticket'))
        self.assertEqual(response.status_code, 302)  # 로그인 페이지로 리다이렉트
    
    def test_buy_ticket_authenticated(self):
        """로그인 후 티켓 구매 페이지 접근"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('buy_ticket'))
        self.assertEqual(response.status_code, 200)
    
    def test_buy_auto_ticket(self):
        """자동 티켓 구매 테스트"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('buy_ticket'), {
            'is_auto': True,
            'numbers': ''
        })
        self.assertEqual(response.status_code, 302)  # 리다이렉트
        self.assertTrue(Ticket.objects.filter(user=self.user, is_auto=True).exists())
    
    def test_buy_manual_ticket(self):
        """수동 티켓 구매 테스트"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('buy_ticket'), {
            'is_auto': False,
            'numbers': '1,2,3,4,5,6'
        })
        self.assertEqual(response.status_code, 302)  # 리다이렉트
        ticket = Ticket.objects.get(user=self.user, is_auto=False)
        self.assertEqual(ticket.numbers, '1,2,3,4,5,6')


class AdminViewTest(TestCase):
    """관리자 뷰 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            password='adminpass123'
        )
        # 테스트용 티켓 생성
        Ticket.objects.create(
            user=self.user,
            numbers="1,2,3,4,5,6",
            is_auto=False
        )
    
    def test_admin_sales_requires_superuser(self):
        """판매 실적은 superuser만 접근 가능"""
        # 일반 사용자
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('admin_sales'), follow=True)
        # user_passes_test는 권한 없을 때 로그인 페이지로 리다이렉트하거나 403 반환
        self.assertIn(response.status_code, [403, 302])  # 권한 없음
        
        # 관리자
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('admin_sales'))
        self.assertEqual(response.status_code, 200)
    
    def test_admin_draw_requires_superuser(self):
        """추첨 진행은 superuser만 접근 가능"""
        # 일반 사용자
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('admin_draw'), follow=True)
        # user_passes_test는 권한 없을 때 로그인 페이지로 리다이렉트하거나 403 반환
        self.assertIn(response.status_code, [403, 302])  # 권한 없음
        
        # 관리자
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('admin_draw'))
        self.assertEqual(response.status_code, 200)
    
    def test_admin_draw_execution(self):
        """추첨 진행 테스트"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('admin_draw'))
        self.assertEqual(response.status_code, 302)  # 리다이렉트
        self.assertTrue(Draw.objects.filter(is_active=True).exists())
    
    def test_admin_winners_requires_superuser(self):
        """당첨자 확인은 superuser만 접근 가능"""
        # 일반 사용자
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('admin_winners'), follow=True)
        # user_passes_test는 권한 없을 때 로그인 페이지로 리다이렉트하거나 403 반환
        self.assertIn(response.status_code, [403, 302])  # 권한 없음
        
        # 관리자
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('admin_winners'))
        self.assertEqual(response.status_code, 200)
