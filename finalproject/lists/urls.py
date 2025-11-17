# urls.py
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # This URL now points to the combined view function and handles both GET and POST
    path('<int:listing_id>', views.listing_detail_view, name='listing_detail'),
    path('add/<int:listing_id>', views.add_to_listing, name='add_to_listing'),
    path('remove/<int:listing_id>', views.remove_from_listing, name='remove_from_listing'),
    # Changed the name to match the view function name
    path('update/<int:listing_id>', views.update_progress, name='update_progress'),
    # Removed: path("comment/<int:listing_id>", views.comment, name = "comment"),
    path('create', views.create, name='create'),
    path('signed_up', views.signed_up, name='signed_up'),
    path('completed', views.completed, name='completed'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
