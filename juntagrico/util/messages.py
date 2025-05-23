from django.template.loader import get_template
from django.utils import timezone

from juntagrico.dao.memberdao import MemberDao


def home_messages(request):
    result = []
    member = request.user.member
    if member.confirmed is False:
        result.append(get_template('messages/not_confirmed.html').render())
    if member.subscription_current is None and member.subscription_future is None:
        result.append(get_template('messages/no_subscription.html').render())
    unpaid_shares = member.share_set.unpaid().count()
    if unpaid_shares > 0:
        template = get_template('messages/unpaid_shares.html')
        render_result = template.render({'amount': unpaid_shares})
        result.append(render_result)
    return result


def job_messages(request, job):
    result = []
    member = request.user.member
    all_participants = list(MemberDao.members_by_job(job))
    if member in all_participants:
        render_dict = {
            'amount': all_participants.count(member) - 1,
        }
        result = [get_template('messages/job_assigned.html').render(render_dict)]
    elif job.canceled:
        result = [get_template('messages/job_canceled.html').render()]
    elif job.end_time() < timezone.now():
        result = [get_template('messages/job_past.html').render()]
    elif job.start_time() < timezone.now():
        result = [get_template('messages/job_running.html').render()]
    elif job.free_slots == 0:
        result = [get_template('messages/job_fully_booked.html').render()]
    return result


def error_message():
    return get_template('messages/error.html').render()


def alert(message):
    if message.level_tag == 'error':
        alert_lvl = 'danger'
    elif message.level_tag == 'debug':
        alert_lvl = 'secondary'
    else:
        alert_lvl = message.level_tag
    return get_template('messages/alert.html').render({'message': message, 'alert_level': 'alert-' + alert_lvl})
