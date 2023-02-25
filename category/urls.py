from django.urls import path
from . import views

app_name = 'category'
urlpatterns = [
    path('', views.ProductView.as_view(), name='products'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product'),
    path('<slug:category_slug>/', views.ProductView.as_view(), name='category_filter'),
    path('reply/<int:post_id>/<int:comment_id>/', views.PostAddReplyView.as_view(), name='post_reply'),
]
