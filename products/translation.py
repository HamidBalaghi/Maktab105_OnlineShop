from modeltranslation.translator import TranslationOptions, translator
from .models import Product, Category


class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'brand', 'description')


class CategoryTranslationOptions(TranslationOptions):
    fields = ('category',)


translator.register(Product, ProductTranslationOptions)
translator.register(Category, CategoryTranslationOptions)
