from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth import  login, logout, authenticate
from django.views.generic.edit import FormView
from django.views import View
from django.core.exceptions import ValidationError
from .forms import LoginForm

      
class LoginView(FormView):
    template_name = 'account/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home:index')
    
    def get_success_url(self):
        # Check if there is a 'next' parameter in the request
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        else:
            return reverse('home:index')
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        
        # First use submitted credentials to authenticate user
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username = username, password = password)
        
        if user is not None:
            
            # If user doesnt have OTP enbled just log them in
            login(self.request, user)
        return super().form_valid(form)
        
class LogoutView(View):

  def get(self, request):
    return render(request, 'account/logout.html', {})

  def post(self, request):
    logout(request)
    return redirect('account:login')
