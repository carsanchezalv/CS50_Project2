from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, AuctionsInfo, Bids, Watchlist, Winner, Comments


def index(request):
    return render(request, "auctions/index.html", {
        "auctionlist": AuctionsInfo.objects.filter(active_bool = True)
    })


def login_view(request):
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Wrong username/password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "The passwords do not match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "This username already exists."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def category(request, category_name):
    cat = AuctionsInfo.objects.filter(category = category_name, active_bool = True)
    return render(request, "auctions/index.html",{
        "auctionlist" : cat
    })
    
def categories(request):
    this_category = AuctionsInfo.objects.values('category').distinct()
    return render(request, "auctions/categories.html",{
        "categories" : this_category
    })

@login_required(login_url='login')
def create(request):
    if request.method == "POST":
        m = AuctionsInfo()
        m.user = request.user.username
        m.title = request.POST["title"]
        m.desc = request.POST["description"]
        m.starting_bid = request.POST["starting_bid"]
        m.image_url = request.POST["img_url"]
        m.category = request.POST["category"]
        m.save()
        return redirect("index")
    return render(request, "auctions/create.html")

def minbid(min_bid, present_bid):
    for bids_list in present_bid:
        if min_bid < int(bids_list.bid):
            min_bid = int(bids_list.bid)
    return min_bid


def listingpage(request, bidid):
    biddesc = AuctionsInfo.objects.get(pk = bidid, active_bool = True)
    bids_present = Bids.objects.filter(listingid = bidid)

    return render(request, "auctions/listing.html",{
        "list": biddesc,
        "comments" : Comments.objects.filter(listingid = bidid),
        "present_bid": minbid(biddesc.starting_bid, bids_present),
    })

def watchlist(request, listing_id):
    
    user = request.user
    l = AuctionsInfo.objects.filter(id = listing_id).first()
    
    w = Watchlist.objects.filter(user = user, listing = l).first()
    
    if w is None:
        wl = Watchlist.objects.create(user = user, listing = l)
        wl.save()
        return HttpResponseRedirect(reverse("watchlist"))
    
    w.delete()
    return HttpResponseRedirect(reverse("watchlist"))

@login_required
def close(request, listing_id):
    
    l = AuctionsInfo.objects.filter(id = listing_id).first()
    b = Bids.objects.filter(listingid = listing_id).first()
    
    if l.user == request.user.username and not b is None:
        l.active_bool = False
        l.winner = b.user
        
        l.save()
        
        return HttpResponseRedirect(reverse('index'))
    
    elif l.user == request.user.username and b is None:
        l.active_bool = False
        
        l.save()
        
        return HttpResponseRedirect(reverse('index'))
    
    else:
        return render(request, "auctions/error.html", {
            "error": "You cannot close other's listings."
        })

@login_required(login_url='login')
def watchlistpage(request, username):
    
    list_ = Watchlist.objects.filter(user = username)
    return render(request, "auctions/watchlist.html",{
        "user_watchlist" : list_,
    })

@login_required(login_url='login')
def showwatchlist(request):
    list_ = Watchlist.objects.filter(user = request.user.username)
    for items in list_:
            return watchlistpage(request, request.user.username)

    return watchlistpage(request, request.user.username)

@login_required(login_url='login')
def addwatchlist(request):
    nid = request.GET["listid"]

    list_ = Watchlist.objects.filter(user = request.user.username)

    for items in list_:
        if int(items.watch_list.id) == int(nid):
            return watchlistpage(request, request.user.username)

    newwatchlist = Watchlist(watch_list = AuctionsInfo.objects.get(pk = nid), user = request.user.username)
    newwatchlist.save()
    messages.success(request, "Item added to watchlist")

    return listingpage(request, nid)


@login_required(login_url='login')
def deletewatchlist(request):
    rm_id = request.GET["listid"]
    list_ = Watchlist.objects.get(pk = rm_id)

    messages.success(request, f"{list_.watch_list.title} is deleted from your watchlist.")
    list_.delete()

    return redirect("index")


@login_required(login_url='login')
def bid(request):
    bid_amnt = request.GET["bid_amnt"]
    list_id = request.GET["list_d"]
    if(bid_amnt):
        
        bids_present = Bids.objects.filter(listingid = list_id)
        startingbid = AuctionsInfo.objects.get(pk = list_id)
        min_req_bid = startingbid.starting_bid
        min_req_bid = minbid(min_req_bid, bids_present)

        if int(bid_amnt) > int(min_req_bid):
            mybid = Bids(user = request.user.username, listingid = list_id , bid = bid_amnt)
            mybid.save()
            messages.success(request, "Bid Placed")
            return redirect("index")
        else:
            messages.warning(request, f"Sorry, {bid_amnt} is less. It should be more than {min_req_bid}$.")
            return listingpage(request, list_id)
    else:
        messages.warning(request, f"Enter a valid number, please")
        return listingpage(request, list_id)

   

@login_required(login_url='login')
def allcomments(request):
    comment = request.GET["comment"]
    username = request.user.username
    list_id = request.GET["listid"]
    new_comment = Comments(user = username, comment = comment, listingid = list_id)
    new_comment.save()
    return listingpage(request, list_id)



def win_ner(request):
    bid_id = request.GET["listid"]
    bids_present = Bids.objects.filter(listingid = bid_id)
    biddesc = AuctionsInfo.objects.get(pk = bid_id, active_bool = True)
    max_bid = minbid(biddesc.starting_bid, bids_present)
    try:
        winner_object = Bids.objects.get(bid = max_bid, listingid = bid_id)
        winner_obj = AuctionsInfo.objects.get(id = bid_id)
        win = Winner(bid_win_list = winner_obj, user = winner_object.user)
        winners_name = winner_object.user
    
    except:
        winner_obj = AuctionsInfo.objects.get(starting_bid = max_bid, id = bid_id)
        win = Winner(bid_win_list = winner_obj, user = winner_obj.user)
        winners_name = winner_obj.user
    biddesc.active_bool = False
    biddesc.save()

    win.save()
    messages.success(request, f"{winners_name} won {win.bid_win_list.title}.")
    return redirect("index")

def winnings(request):
    try:
        your_win = Winner.objects.filter(user = request.user.username)
    except:
        your_win = None

    return render(request, "auctions/winnings.html",{
        "user_winlist" : your_win,
    })