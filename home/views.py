from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import  render

def index(request):
    context = {}
    return(render(request, 'home/index.html', context))

def privacy(request):
    return render(request, 'home/privacy_policy.html', {
        'title': 'Privacy Policy',
        'meta_description': 'Our privacy policy on the use of data, cookies, and opt-out information.',
        'org_name': '<Org Name>',
        'website_url': '<example.com>'})

def terms(request):
    return render(request, 'home/terms_of_service.html', {
        'title' : 'Terms of Service',
        'meta_description': 'Our terms of service for use of our website',
        'org_name': '<Org Name>', 
        'website_url': '<example.com>',
        'org_email': '<person@example.com>'})
