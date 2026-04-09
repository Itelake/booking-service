from datetime import datetime, timedelta
from app.services.utils.time import overlaps


def test_overlap_true_partial():
    a1 = datetime(2026, 1, 1, 10, 0)
    a2 = a1 + timedelta(hours=1)      # 10:00-11:00
    b1 = datetime(2026, 1, 1, 10, 30)
    b2 = b1 + timedelta(hours=1)      # 10:30-11:30
    assert overlaps(a1, a2, b1, b2) is True


def test_overlap_false_touching_border():
    a1 = datetime(2026, 1, 1, 10, 0)
    a2 = datetime(2026, 1, 1, 11, 0)
    b1 = datetime(2026, 1, 1, 11, 0)
    b2 = datetime(2026, 1, 1, 12, 0)
    assert overlaps(a1, a2, b1, b2) is False


def test_overlap_true_one_inside_another():
    a1 = datetime(2026, 1, 1, 10, 0)
    a2 = datetime(2026, 1, 1, 14, 0)
    b1 = datetime(2026, 1, 1, 11, 0)
    b2 = datetime(2026, 1, 1, 12, 0)
    assert overlaps(a1, a2, b1, b2) is True