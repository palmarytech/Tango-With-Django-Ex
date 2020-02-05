from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.utils.decorators import method_decorator

from rango.models import Category
from rango.models import Page
from rango.models import User, UserProfile
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
        context_dict[
            'boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
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
    last_visit_cookie = get_server_side_cookie(request, 'last_visit',
                                               str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
    request.session['visits'] = visits


def get_category_list(max_results=0, starts_with=''):
    category_list = []

    if starts_with:
        category_list = Category.objects.filter(name__istartswith=starts_with)

    if max_results > 0:
        if len(category_list) > max_results:
            category_list = category_list[:max_results]

    return category_list


# !class-base view for show_category
class ShowCategoryView(View):
    def create_context_dict(self, category_name_slug):
        context_dict = {}
        try:
            category = Category.objects.get(slug=category_name_slug)
            pages = Page.objects.filter(category=category).order_by('-views')
            category.views = category.views + 1
            category.save()
            context_dict['pages'] = pages
            context_dict['category'] = category
            context_dict['conn'] = 1
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
                return redirect(
                    reverse('rango:show_category',
                            kwargs={'category_name_slug': category_name_slug}))
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
            selected_page = Page.objects.get(id=page_id)
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
        return render(request, 'rango/profile_registration.html',
                      {'form': form})

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
        return render(request, 'rango/profile_registration.html',
                      {'form': form})


#!base class view for profile


class ProfileView(View):
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        user_profile = UserProfile.objects.get_or_create(user=user)[0]
        form = UserProfileForm({
            'website': user_profile.website,
            'picture': user_profile.picture
        })
        return (user, user_profile, form)

    @method_decorator(login_required())
    def get(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))

        context_dict = {
            'user_profile': user_profile,
            'selected_user': user,
            'form': form
        }
        return render(request, 'rango/profile.html', context_dict)

    @method_decorator(login_required())
    def post(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))

        form = UserProfileForm(request.POST,
                               request.FILES,
                               instance=user_profile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('rango:profile', user.username)
        else:
            print(form.errors)

        context_dict = {
            'user_profile': user_profile,
            'selected_user': user,
            'form': form
        }
        return render(request, 'rango/profile.html', context_dict)


#!base class view for profile list


class ListProfileView(View):
    @method_decorator(login_required())
    def get(self, request):
        profiles = UserProfile.objects.all()

        return render(request, 'rango/list_profile.html',
                      {'user_profile_list': profiles})


#!base class view for like category function
class LikeCategoryView(View):
    @method_decorator(login_required)
    def get(self, request):
        category_id = request.GET['category_id']

        try:
            category = Category.objects.get(id=int(category_id))
        except Category.DoesNotExist:
            return HttpResponse(-1)
        except ValueError:
            return HttpResponse(-1)

        category.likes = category.likes + 1
        category.save()

        return HttpResponse(category.likes)



class ConnSeverView(View):
    def get(self, request):
        connInfo = request.GET['conn_info']
        if int(connInfo) == 1:
            return HttpResponse("connected")
        # return HttpResponse(connInfo)



# !base class view for search category function
class CategorySuggestionView(View):
    def get(self, request):
        if 'suggestion' in request.GET:
            suggestion = request.GET['suggestion']
        else:
            suggestion = ''

        category_list = get_category_list(max_results=8,
                                          starts_with=suggestion)

        if len(category_list) == 0:
            category_list = Category.objects.order_by('-likes')

        return render(request, 'rango/categories.html',
                      {'categories': category_list})


# !base class view for add page form search result
class SearchAddPageView(View):
    @method_decorator(login_required)
    def get(self, request):
        category_id = request.GET['category_id']
        title = request.GET['title']
        url = request.GET['url']

        try:
            category = Category.objects.get(id=int(category_id))
        except Category.DoesNotExist:
            return HttpResponse('Error - category not found.')
        except ValueError:
            return HttpResponse('Error - bad category ID.')

        p = Page.objects.get_or_create(category=category, title=title, url=url)
        pages = Page.objects.filter(category=category).order_by('-views')
        return render(request, 'rango/page_listing.html', {'pages': pages})
