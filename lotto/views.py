from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from django.http import Http404
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from .forms import LottoBuyForm, SignUpForm, LoginForm
from .models import Ticket, Draw
from .utils import calculate_winning_grade
import random

def signup(request):
    """회원가입"""
    if request.user.is_authenticated:
        return redirect('buy_ticket')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '회원가입이 완료되었습니다!')
            return redirect('buy_ticket')
    else:
        form = SignUpForm()
    
    return render(request, 'lotto/signup.html', {'form': form})


def user_login(request):
    """사용자 로그인"""
    if request.user.is_authenticated:
        return redirect('buy_ticket')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'환영합니다, {user.username}님!')
            return redirect('buy_ticket')
    else:
        form = LoginForm()
    
    return render(request, 'lotto/login.html', {'form': form})


def user_logout(request):
    """사용자 로그아웃"""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, '로그아웃되었습니다.')
    return redirect('home')  # 홈페이지로 리다이렉트


def home(request):
    """홈페이지"""
    if request.user.is_authenticated:
        return redirect('buy_ticket')
    return render(request, 'lotto/home.html')


@login_required
def buy_ticket(request):
    if request.method == "POST":
        form = LottoBuyForm(request.POST)
        if form.is_valid():
            is_auto = form.cleaned_data["is_auto"]
            numbers = form.cleaned_data["numbers"]

            if is_auto:
                nums = sorted(random.sample(range(1, 46), 6))
                numbers = ",".join(str(n) for n in nums)

            ticket = Ticket.objects.create(
                user=request.user,
                numbers=numbers,
                is_auto=is_auto
            )

            return redirect("buy_ticket_done", ticket_id=ticket.id)

    else:
        form = LottoBuyForm()

    return render(request, "lotto/buy_ticket.html", {"form": form})


@login_required
def buy_ticket_done(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    # 활성화된 당첨번호 가져오기
    winning_draw = Draw.objects.filter(is_active=True).first()
    winning_grade = 0
    winning_numbers = None
    bonus_number = None

    if winning_draw:
        winning_numbers = winning_draw.numbers
        bonus_number = winning_draw.bonus_number
        
        # 당첨 등급 계산
        ticket_nums = ticket.get_numbers_list()
        draw_nums = winning_draw.get_numbers_list()
        winning_grade = calculate_winning_grade(ticket_nums, draw_nums, bonus_number)
        
        # 티켓에 당첨 등급 저장
        ticket.winning_grade = winning_grade
        ticket.draw = winning_draw
        ticket.save()

    return render(request, "lotto/buy_ticket_done.html", {
        "ticket": ticket,
        "winning_numbers": winning_numbers,
        "bonus_number": bonus_number,
        "winning_grade": winning_grade,
    })


@login_required
def my_tickets(request):
    """내 티켓 목록 보기"""
    tickets = Ticket.objects.filter(user=request.user).order_by('-created_at')
    active_draw = Draw.objects.filter(is_active=True).first()
    
    return render(request, "lotto/my_tickets.html", {
        "tickets": tickets,
        "active_draw": active_draw,
    })


def is_admin(user):
    """관리자 여부 확인 (superuser만 관리 기능 사용 가능)"""
    return user.is_superuser


@user_passes_test(is_admin)
def admin_sales(request):
    """관리자: 판매 실적 확인"""
    total_tickets = Ticket.objects.count()
    auto_tickets = Ticket.objects.filter(is_auto=True).count()
    manual_tickets = Ticket.objects.filter(is_auto=False).count()
    
    # 사용자별 판매 통계
    user_stats = Ticket.objects.values('user__username').annotate(
        ticket_count=Count('id')
    ).order_by('-ticket_count')[:10]
    
    # 날짜별 판매 통계
    from django.db.models.functions import TruncDate
    daily_stats = Ticket.objects.annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('-date')[:30]
    
    return render(request, "lotto/admin_sales.html", {
        "total_tickets": total_tickets,
        "auto_tickets": auto_tickets,
        "manual_tickets": manual_tickets,
        "user_stats": user_stats,
        "daily_stats": daily_stats,
    })


@user_passes_test(is_admin)
def admin_draw(request):
    """관리자: 추첨 진행"""
    if request.method == "POST":
        # 기존 활성 추첨 비활성화
        Draw.objects.filter(is_active=True).update(is_active=False)
        
        # 새 당첨번호 생성
        numbers = sorted(random.sample(range(1, 46), 6))
        bonus = random.choice([n for n in range(1, 46) if n not in numbers])
        
        draw = Draw.objects.create(
            numbers=",".join(str(n) for n in numbers),
            bonus_number=bonus,
            is_active=True
        )
        
        # 모든 티켓에 대해 당첨 등급 계산 및 업데이트
        tickets = Ticket.objects.all()
        for ticket in tickets:
            ticket_nums = ticket.get_numbers_list()
            draw_nums = draw.get_numbers_list()
            winning_grade = calculate_winning_grade(ticket_nums, draw_nums, draw.bonus_number)
            ticket.winning_grade = winning_grade
            ticket.draw = draw
            ticket.save()
        
        messages.success(request, f"추첨이 완료되었습니다! 당첨번호: {draw.numbers}, 보너스: {draw.bonus_number}")
        return redirect("admin_winners")
    
    active_draw = Draw.objects.filter(is_active=True).first()
    return render(request, "lotto/admin_draw.html", {
        "active_draw": active_draw,
    })


@user_passes_test(is_admin)
def admin_winners(request):
    """관리자: 당첨자 확인"""
    active_draw = Draw.objects.filter(is_active=True).first()
    
    if not active_draw:
        messages.info(request, "아직 추첨이 진행되지 않았습니다.")
        return render(request, "lotto/admin_winners.html", {
            "active_draw": None,
            "winners_by_grade": {},
        })
    
    # 등급별 당첨자 통계
    winners_by_grade = {}
    for grade in range(1, 6):
        winners = Ticket.objects.filter(draw=active_draw, winning_grade=grade)
        winners_by_grade[grade] = {
            "count": winners.count(),
            "tickets": winners.select_related('user')[:50],  # 최대 50개만 표시
        }
    
    # 전체 당첨 티켓
    all_winning_tickets = Ticket.objects.filter(
        draw=active_draw,
        winning_grade__gt=0
    ).select_related('user').order_by('-winning_grade', 'created_at')
    
    return render(request, "lotto/admin_winners.html", {
        "active_draw": active_draw,
        "winners_by_grade": winners_by_grade,
        "all_winning_tickets": all_winning_tickets,
    })
