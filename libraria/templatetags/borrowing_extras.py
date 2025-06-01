# libraria/templatetags/borrowing_extras.py

from django import template
from libraria.models import borrowing

register = template.Library()

@register.simple_tag
def get_user_request(user, book):
    """
    Kembalikan object borrowing (first) jika ada request dengan status Pending atau Borrowed,
    untuk kombinasi user + book. Kalau tidak ada, return None.
    """
    return borrowing.objects.filter(
        borrower=user,
        book=book,
        status__in=['Pending','Borrowed']
    ).first()
