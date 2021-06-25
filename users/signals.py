from django.contrib.auth.signals import user_logged_in, user_logged_out


def record_user_logged_in(sender, request, user, **kwargs):
    ''' '''
    user.logged_in = True
    user.save()


def record_user_logged_out(sender, request, user, **kwargs):
    ''' '''
    user.logged_in = False
    user.save()


user_logged_in.connect(record_user_logged_in)
user_logged_out.connect(record_user_logged_out)
