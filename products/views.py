from django.views.generic import DetailView, TemplateView
from products.models import Product, Category
from django.shortcuts import get_object_or_404, redirect


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product.html'

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, pk=self.kwargs.get('pk'), slug=self.kwargs.get('slug'),
                                         is_active=True)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product.product_details()
        return context


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        context['categories'] = dict()
        for category in categories:
            context['categories'][f"{category.category}"] = category.products.filter(stock__gt=0,
                                                                                     is_active=True).order_by(
                '-created_at')
        return context


class CategoryProductView(TemplateView):
    template_name = 'category_products.html'

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(Category, slug=self.kwargs.get('slug'), pk=self.kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        available_available = self.category.products.filter(stock__gt=0, is_active=True).order_by('-created_at')
        unavailable_available = self.category.products.filter(stock__lte=0, is_active=True).order_by('-created_at')

        context['products'] = list(available_available) + list(unavailable_available)
        context['category'] = f"{self.kwargs.get('slug')}"
        return context
