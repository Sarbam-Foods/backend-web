from django.urls import path

from products import views

urlpatterns = [
   path('categories/', views.CategoryListAPIView.as_view(), name='category-list'),
   path('products/', views.ProductListAPIView.as_view(), name='product-list'),

   path('cart/', views.CartListAPIView.as_view(), name='user-cart'),
   path('cart/<int:cart_id>/delete/', views.DeleteCartAPIView.as_view(), name='delete_cart'),
   
   path('cart/item/<int:product_id>/add/', views.AddProductToCartAPIView.as_view(), name='add_to_cart'),
   path('cart/item/<int:product_id>/cancel/', views.CancelCartProductAPIView.as_view(), name='cancel_cart_item'),

   path('order/place/', views.PlaceOrderAPIView.as_view(), name='place_order'),
   path('order/fetch/', views.UserOrdersAPIView.as_view(), name='fetch_orders'),

   path('order/<int:order_id>/cancel/', views.CancelOrderAPIView.as_view(), name='order_cancel'),
   path('order/item/<int:order_item_id>/cancel/', views.CancelOrderItemAPIView.as_view(), name='order_item_cancel'),

   path('deals/combo/', views.ComboDealsAPIView.as_view(), name='combo_deals'),
   path('deals/hot/', views.HotDealsAPIView.as_view(), name='hot_deals'),
]  