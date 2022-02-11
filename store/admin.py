from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from django.urls import reverse
from django.db.models.query import QuerySet
from store import models
from store.models import Collection, Customer, Product, Order
from urllib.parse import urlencode

admin.site.site_header = 'Storepify Admin'
admin.site.index_title = 'Admin'

class InventoryFilter(admin.SimpleListFilter):
  title = 'inventory'
  parameter_name = 'inventory'

  def lookups(self, request, model_admin):
      return [
        ('<10', 'Low')
      ]
      
  def queryset(self, request, queryset: QuerySet):
    if self.value() == '<10':
      return queryset.filter(inventory__lt=10)

      
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  autocomplete_fields = ['collection',]
  prepopulated_fields = {'slug': ('title',)}
  actions = ['clear_inventory',]
  search_fields = ['title']
  list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
  list_editable = ['unit_price']
  list_filter = ['collection', 'last_update', InventoryFilter]
  list_per_page = 10
  list_select_related = ['collection',]


  @admin.display(ordering='inventory')
  def inventory_status(self, product):
    if product.inventory < 10:
      return 'Low'
    return 'Ok'

  
  # Adding custom actions 
  @admin.action(description='Clear Inventory')
  def clear_inventory(self, request, queryset):
    updated_count = queryset.update(inventory=0)
    self.message_user(
      request,
      f'{updated_count} Products were successfully updated.'
    )


  def collection_title(self, product):
    return product.collection.title 


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
  list_display = ['id', 'first_name', 'last_name', 'membership', 'orders']
  list_editable = ['membership',]
  list_per_page = 10
  ordering = ['first_name', 'last_name']
  search_fields = ['first_name__istartswith', 'last_name__istartswith']

  @admin.display(ordering='orders_count')
  def orders(self, customer):
    url = (
      reverse('admin:store_order_changelist')
      + '?'
      + urlencode({
        'customer__id': customer.id
      }))
    return format_html('<a href="{}">{} Orders</a>', url, customer.orders_count)
    
  
  def get_queryset(self, request):
      return super().get_queryset(request).annotate(
        orders_count=Count('order')
      )
  
  

  
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
  list_display = ['title', 'products_count']
  search_fields = ['title']

  @admin.display(ordering='products_count')
  def products_count(self, collection):
    url = (
      reverse('admin:store_product_changelist')
      + '?'
      + urlencode({
        'collection__id': str(collection.id)
      }))
    return format_html('<a href="{}">{}</a>', url, collection.products_count)
    
  # overriding the base queryset
  def get_queryset(self, request):
      return super().get_queryset(request).annotate(products_count=Count('products'))

class OrderItemInline(admin.TabularInline):
  model = models.OrderItem 
  autocomplete_fields = ['product']
  min_num = 1
  max_num = 2
  extra = 0
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
  list_display = ['id', 'placed_at', 'customer'] 
  list_per_page = 10
  inlines = [OrderItemInline]
  autocomplete_fields = ['customer']