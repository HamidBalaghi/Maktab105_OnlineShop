from django.views.generic import DetailView, TemplateView
from products.models import Product, Category
from django.shortcuts import get_object_or_404, redirect
from core.mixin import NavbarMixin


class ProductDetailView(NavbarMixin, DetailView):
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


class HomePageView(NavbarMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        context['categories'] = dict()
        for category in categories:
            context['categories'][category.id] = {
                'name': category.category,
                'products': category.products.filter(stock__gt=0, is_active=True).order_by('-created_at')
            }
        return context


class CategoryProductView(NavbarMixin, TemplateView):
    template_name = 'category_products.html'

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(Category, slug=self.kwargs.get('slug'), pk=self.kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        available = self.category.products.filter(stock__gt=0, is_active=True).order_by('-created_at')
        unavailable = self.category.products.filter(stock__lte=0, is_active=True).order_by('-created_at')

        context['products'] = list(available) + list(unavailable)
        context['category'] = f"{self.kwargs.get('slug')}"
        context['children'] = self.category.child_categories.all()

        return context

#
# class TestView(APIView):
#     def get_queryset(self):
#         user = self.request.user
#         if self.request.method == "GET" and "view_order" in user.groups.values_list("permissions", flat=True):
#             return Order.objects.all()
#         if self.request.method == "GET" and "view_order_mine" in user.groups.values_list("permissions", flat=True):
#             return Order.objects.filter(customer=user)
