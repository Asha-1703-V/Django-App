from django.contrib.sitemaps import Sitemap
from .models import Product

class ShopSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj: Product):
        return obj.created_at