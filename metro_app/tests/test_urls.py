from django.test import SimpleTestCase
from django.urls import reverse, resolve
from metro_app.views import index
from metro_app.road_network.views import list_of_road_networks



class TestUrls(SimpleTestCase):

    def test_home_url_resolve(self):
        url = reverse('home')
        self.assertEquals(resolve(url).func, index)

    def test_list_of_road_networks_url_resolve(self):
        url = reverse('list_of_road_networks', args = ['some-pk'])
        self.assertEquals(resolve(url).func, list_of_road_networks)
