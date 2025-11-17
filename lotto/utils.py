"""
로또 당첨 등급 계산 유틸리티
"""
def calculate_winning_grade(ticket_numbers, draw_numbers, bonus_number=None):
    """
    티켓 번호와 당첨 번호를 비교하여 당첨 등급을 계산
    
    Args:
        ticket_numbers: 티켓 번호 리스트 (예: [1, 5, 12, 20, 33, 42])
        draw_numbers: 당첨 번호 리스트 (예: [1, 5, 12, 20, 33, 42])
        bonus_number: 보너스 번호 (옵션)
    
    Returns:
        int: 당첨 등급 (0: 낙첨, 1: 1등, 2: 2등, 3: 3등, 4: 4등, 5: 5등)
    """
    ticket_set = set(ticket_numbers)
    draw_set = set(draw_numbers)
    
    # 일치하는 번호 개수
    match_count = len(ticket_set & draw_set)
    
    # 당첨 등급 계산
    if match_count == 6:
        return 1  # 1등: 6개 일치
    elif match_count == 5:
        if bonus_number and bonus_number in ticket_set:
            return 2  # 2등: 5개 일치 + 보너스 번호
        else:
            return 3  # 3등: 5개 일치
    elif match_count == 4:
        return 4  # 4등: 4개 일치
    elif match_count == 3:
        return 5  # 5등: 3개 일치
    else:
        return 0  # 낙첨

