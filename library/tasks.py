import logging
from smtplib import SMTPException

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Loan

logger = logging.getLogger('celery_tas')


@shared_task
def send_loan_notification(loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
        member_email = loan.member.user.email
        book_title = loan.book.title
        send_mail(
            subject='Book Loaned Successfully',
            message=f'Hello {loan.member.user.username},\n\nYou have successfully loaned "{book_title}".\nPlease return it by the due date.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
    except Loan.DoesNotExist:
        pass


@shared_task
def check_overdue_loans():
    overdue_loans = Loan.objects.filter(
        is_returned=False, due_date__gt=timezone.now()
    ).select_related('book').select_related('member__user')

    if not overdue_loans:
        logger.info("No overdue member found")
        return

    try:
        for loan in overdue_loans:
            member_user = loan.member.user
            send_mail(
                subject='Reminder',
                message=f'Hello! {member_user.username} Please return your loan, it is overdue',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[member_user.email],
                fail_silently=False,
            )
            logger.debug(f"Sending email to {member_user.email}")
    except SMTPException as e:
        logger.error(f"sending email to user(s) failed. {e}")
