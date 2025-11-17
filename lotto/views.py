from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .forms import LottoBuyForm
from .models import Ticket, Draw
import random

@login_required
def buy_ticket(request):
    if request.method == "POST":
        form = LottoBuyForm(request.POST)
        if form.is_valid():
            is_auto = form.cleaned_data["is_auto"]
            numbers = form.cleaned_data["numbers"]

            if is_auto:
                nums = random.sample(range(1, 46), 6)
                numbers = ",".join(str(n) for n in nums)

            ticket = Ticket.objects.create(
                user=request.user,
                numbers=numbers,
                is_auto=is_auto
            )

            # ⭐ 티켓 ID를 함께 보낸다!
            return redirect("buy_ticket_done", ticket_id=ticket.id)

    else:
        form = LottoBuyForm()

    return render(request, "lotto/buy_ticket.html", {"form": form})


# ⭐ 구매 완료 페이지에서 티켓 번호 표시 가능하도록 수정된 함수
@login_required
def buy_ticket_done(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id, user=request.user)
    except Ticket.DoesNotExist:
        raise Http404("티켓을 찾을 수 없습니다.")

    # 당첨번호 가져오기 (하나만 사용)
    winning_draw = Draw.objects.first()
    is_winner = False
    winning_numbers = None

    if winning_draw:
        winning_numbers = winning_draw.numbers
        # 번호 비교 (정확히 일치해야 당첨)
        ticket_nums = set(int(n.strip()) for n in ticket.numbers.split(','))
        draw_nums = set(int(n.strip()) for n in winning_draw.numbers.split(','))
        is_winner = (ticket_nums == draw_nums)

    return render(request, "lotto/buy_ticket_done.html", {
        "ticket": ticket,
        "winning_numbers": winning_numbers,
        "is_winner": is_winner,
    })
