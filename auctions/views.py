from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from auctions.models import *
from auctions.models import User

# Index view
def index(request):
    return render(request, "auctions/index.html", {
        #All active listings objects
        'listings': Listings.objects.all()
    })

#Listing dynamic page
@login_required
def listing(request, listing_id):
    listing = Listings.objects.filter(id=listing_id).get()
    bids = Bids.objects.filter(listing=listing_id).order_by('-id').all()
    most_valuable_bids = bids.order_by('-value')[0:1]
    listing_in_watchlist = Watchlists.objects.filter(user=request.user, listing=listing)
    comments = Comments.objects.filter(listing=listing)

    context = {
        "listing": listing,
        "bids": bids,
        "last_user_bids": bids.filter(user=request.user)[0:1],
        "most_valuable_bids": most_valuable_bids,
        "listing_in_watchlist": listing_in_watchlist,
        "comments": comments,
        "bid_placed": False,
        "bid_error": False,
    }

    if request.method == "POST":
        user_bid = request.POST.get("user_bid")
        delete_listing = request.POST.get("delete_listing")
        close_auction = request.POST.get("close_auction")
        add_to_watchlist = request.POST.get("add_to_watchlist")
        comment = request.POST.get("comment")

        #update the variables
        bids = Bids.objects.filter(listing=listing_id).order_by('-id').all()
        most_valuable_bids = bids.order_by('-value')[0:1]


        #Verify id the user placed a bid
        if user_bid:
            user_bid = float(user_bid)

            if bids:
                for bid in most_valuable_bids:
                    if user_bid > bid.value:
                        Bids.objects.create(
                            user = request.user,
                            listing = listing,
                            value = user_bid
                        ).save()

                        context["bid_placed"] = True
                    else:
                        context["bid_error"] = f"The bid must be greater than the last bid ${bid.value}"    
                        context["bid_placed"] = False
            else:
                if user_bid >= listing.starting_bid:
                    Bids.objects.create(
                        user = request.user,
                        listing = listing,
                        value = user_bid
                    ).save()

                    context["bid_placed"] = True
                else:
                    context["bid_error"] = f"The bid must be greater than the starting bid ${listing.starting_bid}"
                    context["bid_placed"] = False



        #if the hidden input (delete_listing) is submited...
        if delete_listing:
            #then the object that contains the listing is deleted
            Listings.objects.filter(id=listing_id).delete()

            #And the user is redirected to (index) page
            return HttpResponseRedirect(reverse('index'))


        #Verify if the POST return the input-hidden (close_auction)
        if close_auction:
            #Set the status (active) to False
            listing.status = False
            listing.winner_bid = Bids.objects.filter(id=close_auction).get()
            listing.save()


        #Verify if the POST return the input-hidden (add_to_watchlist)
        if add_to_watchlist:
            #And create the watchlist object for the user
            Watchlists.objects.create(
                listing = listing,
                user = request.user
            )
        #Redirect to watchlist
            return HttpResponseRedirect(reverse('watchlist'))


        #Verify if it has a comment
        if comment:
            Comments.objects.create(
                user=request.user,
                listing=listing,
                comment=comment,
            )


    return render(request, "auctions/listing.html", context)


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Categories.objects.all()
    })


def category(request, category):
    return render(request, "auctions/category.html", {
        "category": category,
        "category_items": Listings.objects.filter(category__name=category)
    })


def watchlist(request):
    if request.method == "POST":
        delete_item = request.POST.get("delete_item")

        if delete_item:
            Watchlists.objects.filter(id=delete_item).delete()

    return render(request, "auctions/watchlist.html", {
        "watchlist": Watchlists.objects.filter(user=request.user).all()
    })


def won_auctions(request):
    listings = Listings.objects.filter(winner_bid__user=request.user).all()

    return render(request, "auctions/won_auctions.html", {
        "listings": listings
    })


def create_listing(request):
    if request.method == "POST":
        listing = Listings.objects.create(

            user = request.user,
            title = request.POST.get("title"),
            card_description = request.POST.get("card_description"),
            description = request.POST.get("description"),
            starting_bid = request.POST.get("starting_bid"),
            image_url = request.POST.get("image_url"),
            category = Categories.objects.filter(
                    name=request.POST.get("category")).get()
        )
        listing.save()

        return HttpResponseRedirect(reverse('index'))

    return render(request, "auctions/create_listing.html", {
        "categories": Categories.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
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

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
