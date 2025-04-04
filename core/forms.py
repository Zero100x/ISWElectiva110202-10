"""
Core application forms.

This file defines custom forms used in the application,
primarily for authentication and user management.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError

class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form.
    
    Extends Django's AuthenticationForm to add:
    - Custom styling for fields
    - Additional validation
    - Custom error messages
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Username',
            'autofocus': True
        }),
        error_messages={
            'required': 'Please enter your username'
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Password'
        }),
        error_messages={
            'required': 'Please enter your password'
        }
    )
    
    error_messages = {
        'invalid_login': 'Incorrect username or password. Please try again.',
        'inactive': 'This account is inactive. Please contact the administrator.',
    }
    
    def clean(self):
        """
        Custom form validation.
        
        Verifies that both username and password are provided
        before attempting authentication.
        """
        username = self.cleaned_data.get('username', '')
        password = self.cleaned_data.get('password', '')
        
        if not username:
            raise ValidationError('Username field cannot be empty')
        
        if not password:
            raise ValidationError('Password field cannot be empty')
            
        return super().clean()

class CustomPasswordResetForm(PasswordResetForm):
    """
    Custom password reset request form.
    
    Extends Django's PasswordResetForm to add:
    - Custom styling
    - Additional validation to verify email exists
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Email'
        }),
    )
    
    def clean_email(self):
        """
        Email field validation.
        
        Verifies that the provided email is registered in the system.
        """
        email = self.cleaned_data.get('email')
        if not self.get_users(email):
            raise ValidationError('This email address is not registered in our system.')
        return email

class CustomSetPasswordForm(SetPasswordForm):
    """
    Custom form for setting a new password.
    
    Used in the password reset process to set a new password.
    Extends Django's SetPasswordForm with custom styling.
    """
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'New Password'
        }),
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Confirm New Password'
        }),
    )
