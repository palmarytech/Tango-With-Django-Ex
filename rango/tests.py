from django.test import TestCase
from rango.models import Category
from django.urls import reverse

# Create your tests here.
class CategoryMethodTests(TestCase):
    def test_ensure_views_are_positive(self):
        category = Category(name='test', views=-1, likes=0)
        category.save()

        self.assertEqual((category.views>=0), True)

    
    def test_slug_line_creation(self):
        category = Category(name='Random Category String')
        category.save()

        self.assertEqual(category.slug, 'random-category-string')

class IndexViewTest(TestCase):
    def test_index_view_with_no_categories(self):
        response = self.client.get(reverse('rango:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are no categories present.')
        self.assertQuerysetEqual(response.context['categories'], [])

    def test_index_view_with_categories(self):
        add_category('lisp', 1, 1)
        add_category('Erlang', 1, 1)

        response = self.client.get(reverse('rango:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lisp')
        self.assertContains(response, 'Erlang')

        num_categories = len(response.context['categories'])
        self.assertEqual(num_categories, 2)



def add_category(name, views=0, likes=0):
    category = Category.objects.get_or_create(name=name)[0]
    category.views = views
    category.likes = likes
    category.save()

    return category
