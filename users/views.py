from django.contrib.auth import authenticate, login
from django.views.generic.edit import CreateView
from django.urls.base import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from users import models, forms


class UserRegister(CreateView):
    ''' '''

    model = models.User
    success_url = reverse_lazy('index')
    template_name = 'registration/login.html'
    form_class = forms.UserRegisterForm

    def get_context_data(self, **kwargs):
        ''' '''
        context = super().get_context_data(**kwargs)
        context['reg_form'] = context['form']
        del context['form']
        return context

    def form_valid(self, form):
        ''' '''
        ret = super().form_valid(form)
        user = authenticate(
            self.request,
            username=self.object.email,
            password=form.cleaned_data['password1']
        )
        if user is not None:
            login(self.request, user)
        return ret

    def get(self, request, *args, **kwargs):
        ''' '''
        if request.user.is_authenticated:
            return redirect('index')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        ''' '''
        if request.user.is_authenticated:
            return redirect('index')
        return super().post(request, *args, **kwargs)


@login_required
def list_ready_users(request):
    ''' '''
    return JsonResponse({
        'success': True,
        'users': [
            {'id': user.id, 'email': user.email, 'status': user.get_status()}
            for user in models.User.objects.get_logged()
            if request.user != user
        ]
    })
