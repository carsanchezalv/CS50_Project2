from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category_name>", views.category, name="category"),
    path("create", views.create, name = "create"),
    path("close/<int:listing_id>", views.close, name = "close"),
    path("bidlist", views.bid, name="bid"),
    path("auctions/<int:bidid>", views.listingpage, name="listingpage"),
    path("watchlist/<int:listing_id>", views.watchlist, name = "watchlist"),
    path("added", views.addwatchlist, name = "addwatchlist"),
    path("showwatchlist", views.showwatchlist, name = "showwatchlist"),
    path("comments", views.allcomments, name="allcomments"),
    path("win_ner", views.win_ner, name="win_ner"),
    path("deletewatchlist", views.deletewatchlist, name="deletewatchlist")
]