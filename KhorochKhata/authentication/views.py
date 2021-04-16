import json
import token

from django.contrib.auth.models import User
from django.urls import reverse
from validate_email import validate_email
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib import auth

from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .utils import account_activation_token
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading


# Create your views here.
class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently = False)


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({
                'username_error': 'username should only contain alphanumeric character.'
            }, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'username_error': 'username already in use'
            }, status=409)

        return JsonResponse({'username_valid': True})


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']

        if not validate_email(email):
            return JsonResponse({
                'email_error': 'Email is invalid'
            }, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'email_error': 'Email already in use'
            }, status=409)

        return JsonResponse({'email_valid': True})


class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        # Get User Data
        # Validate
        # Create a user Account
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():

                if len(password) < 8:
                    messages.error(request, "Password too Short")
                    return render(request, 'authentication/register.html', context)

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()

                # path to the view
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

                domain = get_current_site(request).domain
                link = reverse('activate', kwargs={
                    'uidb64': uidb64,
                    'token': account_activation_token.make_token(user)
                })
                activate_urls = 'http://' + domain + link
                email_subject = 'Hi ' + user.username
                email_body = 'Please use this link to verify your account\n' + activate_urls + '\nThanks for being with us.'
                email = EmailMessage(
                    email_subject,
                    email_body,
                    'noreply@khorochkhata.com',
                    [email],
                )
                EmailThread(email).start()
                messages.success(request,
                                 "Account Successfully Created.\n Please go to your mail and activate your account.")
                return render(request, 'authentication/register.html')

        return render(request, 'authentication/register.html')


class VerificationView(View):
    def get(self, request, uidb64, token):

        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login' + '?message=' + 'User already activated.')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated Successfully')

        except Exception as ex:
            pass

        return redirect('login')


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome, ' + user.username + 'You are now logged in.')
                    return redirect('khoroch')
                messages.error(request, 'Account is not active, please check your email.')
                return render(request, 'authentication/login.html')
            messages.error(request, 'Invalid Credentials Please Try Again.')
            return render(request, 'authentication/login.html')
        messages.error(request, 'Please fill all the field.')
        return render(request, 'authentication/login.html')


class LogoutWindow(View):

    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been successfully logged out')
        return redirect('login')


class RequestPasswordResetEmail(View):

    def get(self, request):
        return render(request, 'authentication/reset-password.html')

    def post(self, request):
        email = request.POST['email']
        context = {
            'values': request.POST
        }

        if not validate_email(email):
            messages.error(request, 'Please Provide a valid email.')
            return render(request, 'authentication/reset-password.html', context)

        user = User.objects.filter(email=email)
        print(user)
        if user.exists():

            uidb64 = urlsafe_base64_encode(force_bytes(user[0].pk))
            domain = get_current_site(request).domain
            token = PasswordResetTokenGenerator().make_token(user[0])
            link = reverse('reset-user-password', kwargs={
                'uidb64': uidb64,
                'token': token,
            })
            reset_urls = 'http://' + domain + link
            email_subject = 'Password Reset Instruction ' + user[0].username
            email_body = 'Please use this link to reset your password.\n' + reset_urls + '\nThanks for being with us.'
            email = EmailMessage(
                email_subject,
                email_body,
                'noreply@khorochkhata.com',
                [email],
            )
            EmailThread(email).start()
            messages.success(request, 'We have sent you an email to reset the password. ')
        return render(request, 'authentication/reset-password.html')


class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, 'Password Link is Invalid, Request for a new one')
                return render(request, 'authentication/reset-password.html')

        except Exception as identifier:
            pass

        return render(request, 'authentication/set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }

        password0 = request.POST['password0']
        password1 = request.POST['password1']

        if password0 != password1:
            messages.error(request, 'Password Did not match.')
            return render(request, 'authentication/set-new-password.html', context)
        if len(password0) < 8:
            messages.error(request, 'Password Should Be Atleast 8 Character Long. ')
            return render(request, 'authentication/set-new-password.html', context)

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password0)
            user.save()
            messages.success(request, "Password Reset Successfully. You can Log In now")
            return redirect('login')
        except Exception as identifier:
            messages.info(request, "Something went wrong")
            return render(request, 'authentication/set-new-password.html', context)
