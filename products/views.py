from django.views.generic import DetailView, TemplateView
from products.models import Product, Category
from django.shortcuts import get_object_or_404, redirect


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product.html'

    # context_object_name = 'product'

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, pk=self.kwargs.get('pk'), slug=self.kwargs.get('slug'))

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
            context['categories'][f"{category.category}"] = category.products.all()
        return context
