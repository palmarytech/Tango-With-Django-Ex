from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.utils.decorators import method_decorator

from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm
from rango.bing_search import run_query
from django.views import View

# !IndexView Class-View
class IndexView(View):
    def get(self, request):
        category_list = Category.objects.order_by('-likes')[:5]
        page_list = Page.objects.order_by('-views')[:5]
        context_dict = {}
        context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
        context_dict['categories'] = category_list
        context_dict['pages'] = page_list
        return render(request, 'rango/index.html', context_dict)

#!AboutView Class-View
class AboutView(View):
    def get(self, request):
        context_dict = {}
        visitor_cookie_handler(request)
        context_dict['visits'] = request.session['visits']
        return render(request, 'rango/about.html', context_dict)


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', 1))
    last_visit_cookie = get_server_side_cookie(
        request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(
        last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
    if(datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
    request.session['visits'] = visits


# !class-base view for show_category
class ShowCategoryView(View):
    def create_context_dict(self, category_name_slug):
        context_dict = {}
        try:
            category = Category.objects.get(slug=category_name_slug)
            pages = Page.objects.filter(category=category).order_by('-views')
            context_dict['pages'] = pages
            context_dict['category'] = category
        except Category.DoesNotExist:
            context_dict['pages'] = None
            context_dict['category'] = None
        return context_dict


    def get(self, request, category_name_slug):
        context_dict = self.create_context_dict(category_name_slug)
        return render(request, "rango/category.html", context_dict)

    @method_decorator(login_required())
    def post(self, request, category_name_slug):
        context_dict = self.create_context_dict(category_name_slug)
        query = ''
        query = request.POST['query'].strip()
        if query:
            context_dict['result_list'] = run_query(query)
            context_dict['query'] = query
        return render(request, "rango/category.html", context_dict)
        
# !class-base view for add_category
class AddCategoryView(View):
    @method_decorator(login_required())
    def get(self, request):
        form = CategoryForm()
        return render(request, 'rango/add_category.html', {'form': form})

    @method_decorator(login_required())
    def post(self, request):
        form = CategoryForm(request.POST)

        if form.is_valid:
            form.save(commit=True)
            return redirect(reverse('rango:index'))

        else:
            print(form.errors)

        return render(request, "rango/add_category.html", {'form': form})



# !class-view for add_page
class AddPageView(View):
    def create_context_dict(self, category_name_slug):
        context_dict = {}
        try:
            category = Category.objects.get(slug=category_name_slug)
            form = PageForm()
            context_dict['category'] = category
            context_dict['form'] = form
        except Category.DoesNotExist:
            context_dict['category'] = None
        return context_dict


    @method_decorator(login_required())
    def get(self, request, category_name_slug):
        context_dict = self.create_context_dict(category_name_slug)
        if context_dict['category'] == None:
            return redirect(reverse('rango:index'))
        return render(request, 'rango/add_page.html', context_dict)
        

    @method_decorator(login_required())
    def post(self, request, category_name_slug):
        context_dict = self.create_context_dict(category_name_slug)
        form = PageForm(request.POST)
        if form.is_valid():
            if context_dict['category']:
                page = form.save(commit=False)
                page.category = context_dict['category']
                page.views = 0
                page.save()
                context_dict['form'] = form
                return redirect(reverse('rango:show_category',kwargs={'category_name_slug':category_name_slug }))
        else:
            print(form.errors)
        return render(request, 'rango/add_page.html', context_dict)

# !base class view for restriction function
class RestricteView(View):
    @method_decorator(login_required())
    def get(self, request):
        return render(request, 'rango/restricted.html')


# !base class view for goto_url function
# ?The function handle the page views
class GotoUrlView(View):
    def get(self, request):
        page_id = None
        page_id = request.GET.get('page_id')
        
        try:
            selected_page = Page.objects.get(id = page_id)
        except Page.DoesNotExist:
            return redirect(reverse('rango:index'))
        selected_page.views = selected_page.views + 1
        selected_page.save()
        return redirect(selected_page.url)


# !base class view for register_profile function
# ?the function handle the user info by custom define
class RegisterProfileView(View):
    @method_decorator(login_required())
    def get(self, request):
        form = UserProfileForm()
        return render(request, 'rango/profile_registration.html', {'form': form})


    @method_decorator(login_required())
    def post(self, request):
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)
        return render(request, 'rango/profile_registration.html', {'form': form})
