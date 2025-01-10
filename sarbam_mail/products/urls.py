from django.urls import path

from products import views

urlpatterns = [
   path('categories/', views.CategoryListAPIView.as_view(), name='category-list'),
   path('products/', views.ProductListAPIView.as_view(), name='product-list'),

   path('cart/', views.CartListAPIView.as_view(), name='user-cart'),
   path('cart/<int:cart_id>/delete/', views.DeleteCartAPIView.as_view(), name='delete_cart'),
   
   path('cart/item/<int:product_id>/add/', views.AddProductToCartAPIView.as_view(), name='add-to-cart'),
   path('cart/item/<int:product_id>/delete/', views.DeleteCartProductAPIView.as_view(), name='delete_cart_item'),

   path('order/place/', views.PlaceOrderAPIView.as_view(), name='place_order'),
   path('order/fetch/', views.UserOrdersAPIView.as_view(), name='fetch_orders'),
]  