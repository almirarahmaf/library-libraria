from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.urls import reverse
from django.views.decorators.cache import cache_control
from datetime import timedelta
from django.utils import timezone
from django.utils.timezone import now
from django.db.models import Avg
from itertools import zip_longest
import math

from datetime import date

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from .decorators import unauthenticated_user, allowed_users, admin_only

from .models import Profile, booklist, review_user, ReviewWeb, category, borrowing, review_book
from .forms import CreateUserForm, ProfileForm, ReviewWebForm, addbookForm

import logging
logger = logging.getLogger(__name__)

# Firstpage
@unauthenticated_user
def firstpage(request):
    all_reviews = ReviewWeb.objects.all()
    return render(request, 'libraria/firstpage.html', {
        'all_reviews': all_reviews,
        'request': request})

# Review Web
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def review_web(request):
    if request.method == 'POST':
        form = ReviewWebForm(request.POST)
        if form.is_valid():
            form.save()
            logout(request)
            return redirect('firstpage')
    else:
        form = ReviewWebForm()
    return render(request, 'libraria/review-web.html', {'form': form})

# Signup
@unauthenticated_user
def signupPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()

            group = Group.objects.get(name='user')
            user.groups.add(group)
            login(request, user)
            return redirect('completeProfile')

    context = {'form':form}
    return render(request, 'libraria/signup.html', context)

# Login
@unauthenticated_user
def loginPage(request):
    username = request.COOKIES.get('username', '') 
    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        username_post = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        user = authenticate(request, username=username_post, password=password)
        next_url = request.POST.get('next')

        if user is not None:
            login(request, user)

            if remember == 'on':
                request.session.set_expiry(1209600)  
            else:
                request.session.set_expiry(0)

            if next_url:
                redirect_url = next_url
            elif user.groups.filter(name='user').exists():
                redirect_url = reverse('dashboard')

            response = redirect(redirect_url)

            if remember == 'on':
                response.set_cookie('username', username_post, max_age=1209600) 
            else:
                response.delete_cookie('username') 

            return response
        else:
            messages.info(request, 'Username or password is incorrect')

    context = {
        'username': username,
        'next': next_url
        }
    return render(request, 'libraria/login.html', context)

# Complete Profile
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def completeProfile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)  
            profile.signup = request.user      
            profile.save()                     
            return redirect('login')
    else:
        form = ProfileForm()

    return render(request, 'libraria/complete_profile.html', {'form': form})

# Logout
@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    response = redirect('firstpage')
    return response

#Dashboard
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def dashboard(request):
    user_profile = Profile.objects.get(signup=request.user)
    categories = category.objects.all()
    # borrowings = borrowing.objects.all()
    borrowings = borrowing.objects.filter(borrower=request.user, status='Borrowed').select_related('book')
    book_of_the_month = booklist.objects.annotate(avg_rating=Avg('review_book__rating')).order_by('-avg_rating')[:3]
    
    for book_item in book_of_the_month:
        avg_rating = book_item.avg_rating or 0  
        book_item.full_stars = list(range(int(avg_rating)))  
        book_item.empty_stars = list(range(5 - int(avg_rating)))  

    recommendation = booklist.objects.annotate(avg_rating=Avg('review_book__rating')).filter(avg_rating__gte=3, avg_rating__lte=5).order_by('?')[:6]
    
    for book_item in recommendation:
        avg_rating = book_item.avg_rating or 0  
        book_item.full_stars = list(range(int(avg_rating))) 
        book_item.empty_stars = list(range(5 - int(avg_rating))) 
    
    library_stars = Profile.objects.annotate(total_rating=Avg('signup__reviews_received__rating')).order_by('-total_rating')[:5]

    for user_obj in library_stars:
        total_rating = user_obj.total_rating or 0  
        user_obj.full_stars = list(range(int(total_rating))) 
        user_obj.empty_stars = list(range(5 - int(total_rating)))
        
    context = {
        'borrowings': borrowings,
        'book_of_the_month': book_of_the_month,
        'recommendation': recommendation,
        'library_stars': library_stars,
        'categories':categories,
        'user_profile': user_profile,
    }

    
    return render(request, 'libraria/dashboard.html', context)

# Profile
@allowed_users(allowed_roles=['user'])
@login_required(login_url='login')
def profile(request):
    user_profile = Profile.objects.get(signup=request.user)
    all_reviews = review_user.objects.filter(reviewee=request.user).select_related('reviewer__profile')
    total_reviews = all_reviews.count()

    average_rating = sum(review.rating for review in all_reviews) / total_reviews if total_reviews > 0 else 0
    books = booklist.objects.filter(librender=request.user)

    seen = set()
    unique_reviews = []
    for review in all_reviews:
        key = (review.reviewer_id, review.comment.strip().lower())
        if key not in seen:
            seen.add(key)
            unique_reviews.append(review)


    context = {
        'user_profile': user_profile,
        'join_date': request.user.date_joined,
        'reuser': unique_reviews, 
        'average_rating': average_rating,
        'books': books,
    }

    return render(request, 'libraria/profile.html', context)

# Profile User Lain
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def user_profile(request, user_id):
    try:
        user_profile = Profile.objects.get(signup__id=user_id)
        def chunk_reviews(reviews, size=3):
            args = [iter(reviews)] * size
            return [list(filter(None, chunk)) for chunk in zip_longest(*args)]

        reuser = review_user.objects.filter(reviewee=user_profile.signup)
        total_reviews = reuser.count()

        if total_reviews > 0:
            total_rating = sum(review.rating for review in reuser)
            average_rating = total_rating / total_reviews
        else:
            average_rating = 0

        books = booklist.objects.filter(librender=user_profile.signup)

        review_chunks = chunk_reviews(reuser, size=3)

        context = {
            'user_profile': user_profile,
            'join_date': user_profile.signup.date_joined,
            'reuser': reuser,
            'average_rating': average_rating,
            'books': books,
            'review_chunks': review_chunks,
        }
        return render(request, 'libraria/profile.html', context)
    except Profile.DoesNotExist:
        return HttpResponse("User not found", status=404)

# Edit Profile
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def editProfile(request):
    user_profile = Profile.objects.get(signup=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
        else:
            form = ProfileForm(instance=user_profile)

    context = {
        'user_profile': user_profile,
    }

    return render(request, 'libraria/editProfile.html', context)

# Change Password
@login_required
@allowed_users(allowed_roles=['user'])
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) 
            messages.success(request, 'Password changed successfully.')
            return redirect('editProfile') 
        else:
            messages.error(request, 'An error occurred. Please try again.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'libraria/change_password.html', {'form': form})

# Admin
@login_required(login_url='login')
@admin_only
def admin(request):
    return render(request, 'libraria/admin.html')

# Librender
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def librender(request):
    user_profile = Profile.objects.get(signup=request.user)
    books = booklist.objects.filter(librender=user_profile.signup)
    return render(request, 'libraria/librender.html', {
        'books': books,
        'user_profile': user_profile,
    })

# Request Book
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def request_book(request):
    user_profile = Profile.objects.get(signup=request.user)
    pending_requests = borrowing.objects.filter(
        status='Pending',
        book__librender=request.user
    ).select_related('borrower', 'book')

    pending_fines = borrowing.objects.filter(
        status='FinePending',
        book__librender=request.user
    ).select_related('borrower', 'book')

    context = {
        'pending_requests': pending_requests,
        'pending_fines': pending_fines,
        'user_profile' : user_profile,
    }
    return render(request, 'libraria/request.html', context)
    
# Accept Borrow
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def accept_borrow(request, pk):
    borrow = get_object_or_404(borrowing, borrowing_id=pk, book__librender=request.user)

    if borrow.status == 'Pending' and borrow.book.stock > 0:
        borrow.status = 'Borrowed'
        borrow.book.stock -= 1
        borrow.book.save(update_fields=['stock'])
        borrow.save(update_fields=['status'])
        messages.success(request, "Borrow request accepted. Book is now Borrowed.")
        return redirect('request')

    if borrow.status == 'FinePending':
        if borrow.is_fine_paid:
            borrow.status = 'Returned'
            borrow.return_date = date.today()
            borrow.save(update_fields=['status','return_date'])
            book = borrow.book
            book.stock += 1
            book.save(update_fields=['stock'])
            messages.success(request, "Fine validated. Book has been returned.")
        else:
            messages.error(request, "Fine proof belum ter‐upload atau belum valid.")
        return redirect('request')
    
    messages.error(request, "Tidak bisa mem‐process request ini.")
    return redirect('request')

# Decline Borrow
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def decline_borrow(request, pk):
    borrow = get_object_or_404(borrowing, borrowing_id=pk, book__librender=request.user)

    if borrow.status == 'Pending':
        borrow.status = 'Declined'
        borrow.save(update_fields=['status'])
        messages.info(request, "Borrow request has been declined.")
        return redirect('request')

    if borrow.status == 'FinePending':
        borrow.status = 'Borrowed'
        borrow.fine_proof = None
        borrow.is_fine_paid = False
        borrow.save(update_fields=['status','fine_proof','is_fine_paid'])
        messages.info(request, "Fine proof ditolak. Borrower harus upload ulang bukti denda.")
        return redirect('request')

    messages.error(request, "Tidak bisa mem‐process decline ini.")
    return redirect('request')

# List
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def list_view(request):
    user_profile = Profile.objects.get(signup=request.user)
    borrowings = borrowing.objects.select_related('borrower', 'book').filter(book__librender=request.user)
    return render(request, 'libraria/list.html', {
        'borrowings': borrowings,
        'user_profile' : user_profile,
    })

# Delete Borrowing
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def delete_borrowing(request, pk):
    borrow = get_object_or_404(borrowing, pk=pk)
    borrow.delete()
    messages.success(request, 'Borrowing deleted.')
    return redirect('list_view')

# Add Book
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addbook(request):
    user_profile = Profile.objects.get(signup=request.user)
    if request.method == 'POST':
        form = addbookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.librender = request.user
            form.save()
            return redirect ('librender')
    else:
        form = addbookForm()

    categories = category.objects.all()
    return render(request, 'libraria/addbook.html', {'form': form, 'categories': categories, 'user_profile': user_profile,})

# Edit Book
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def editbook(request, book_id):
    user_profile = Profile.objects.get(signup=request.user)
    book = get_object_or_404(booklist, book_id = book_id)
   
    if request.method == 'POST':
        form = addbookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect('librender')
    else:
        form = addbookForm(instance=book)

    return render(request, 'libraria/editbook.html', {'form': form, 'book': book, 'user_profile': user_profile,})

# Delete Book
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def deletebook(request, book_id):
    book = get_object_or_404(booklist, book_id = book_id)

    if request.method == 'POST':
        book.delete()
        return redirect('librender')
    else:
        return redirect('libbrender')
    
# Validate Fine
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def validate_fine(request, borrowing_id):
    borrow_req = get_object_or_404(borrowing, borrowing_id=borrowing_id)

    if request.user != borrow_req.book.librender:
        messages.error(request, "Anda tidak berhak memvalidasi denda ini.")
        return redirect('rak_pinjam')

    if borrow_req.status != 'FinePending':
        messages.error(request, "Tidak ada denda yang perlu divalidasi untuk transaksi ini.")
        return redirect('rak_pinjam')

    borrow_req.is_fine_paid = True
    borrow_req.status = 'Borrowed'
    borrow_req.save(update_fields=['is_fine_paid', 'status'])
    messages.success(request, "Denda telah divalidasi. Peminjam dapat mengembalikan bukunya sekarang.")
    return redirect('rak_pinjam')

# Halaman Peminjaman
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def halamanpinjam(request, book_id):
    if not request.user.is_authenticated:
        return redirect('login')  

    selected_book = get_object_or_404(booklist, book_id=book_id)
    librarian_user = selected_book.librender
    librarian_profile = Profile.objects.get(signup=librarian_user)

    last_request = (
        borrowing.objects
        .filter(borrower=request.user, book=selected_book)
        .order_by('-borrow_date')
        .first()
    )

    existing_request = (
        borrowing.objects
        .filter(borrower=request.user, book=selected_book, status__in=['Pending', 'Borrowed'])
        .first()
    )

    review_qs = (
        review_book.objects
        .filter(booktitle=selected_book)
        .order_by('booktitle_id')
    )

    review_list = list(review_qs)

    review_chunks = [review_list[i : i + 3] for i in range(0, len(review_list), 3)]

    avg_rating = review_qs.aggregate(avg=Avg('rating'))['avg'] or 0.0
    full_stars = int(math.floor(avg_rating))
    has_half   = (avg_rating - full_stars) >= 0.5

    shipping_cost = 7500
    total_price   = selected_book.price + shipping_cost

    context = {
        'selected_book':     selected_book,
        'librarian_profile': librarian_profile,
        'existing_request':  existing_request,
        'last_request':      last_request,
        'review_chunks':     review_chunks,   
        'full_stars':        full_stars,
        'has_half':          has_half,
        'shipping_cost':     shipping_cost,
        'total_price':       total_price,
    }
    return render(request, 'libraria/halaman_peminjaman.html', context)

# Peminjaman buku
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def borrow_book(request, book_id):
    selected_book     = get_object_or_404(booklist, book_id=book_id)
    librarian_profile = Profile.objects.get(signup=selected_book.librender)
    existing_request  = borrowing.objects.filter(
                           borrower=request.user,
                           book=selected_book,
                           status__in=['Pending','Borrowed']
                        ).first()

    if selected_book.stock <= 0:
        messages.error(request, "Maaf, stok buku sedang habis.")
        return redirect('halamanpinjam', book_id=book_id)

    if request.method == 'POST':
        duration_str  = request.POST.get('duration_weeks')
        payment_file  = request.FILES.get('payment_proof')
        try:
            duration_weeks = int(duration_str)
            if duration_weeks < 1:
                raise ValueError
        except (TypeError, ValueError):
            messages.error(request, "Durasi peminjaman tidak valid.")
            return redirect('halamanpinjam', book_id=book_id)

        if not payment_file:
            messages.error(request, "Bukti pembayaran wajib diunggah.")
            return redirect('halamanpinjam', book_id=book_id)

        today                = timezone.now().date()
        due_date    = today + timedelta(weeks=duration_weeks)

        if existing_request and existing_request.status == 'Pending':
            existing_request.payment_proof = payment_file
            existing_request.due_date   = due_date
            existing_request.save()
            messages.success(request, "Bukti pembayaran berhasil diunggah. Tunggu konfirmasi pemilik.")
            return redirect('halamanpinjam', book_id=book_id)

        new_borrow = borrowing.objects.create(
            borrower = request.user,
            book = selected_book,
            due_date = due_date,
            status = 'Pending',
            payment_proof = payment_file
        )
        messages.success(request, "Permintaan peminjaman berhasil. Tunggu konfirmasi pemilik.")
        return redirect('halamanpinjam', book_id=book_id)

    return redirect('halamanpinjam', book_id=book_id)

# Pengembalian Buku
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def return_book(request, borrowing_id):
    borrow_req = get_object_or_404(borrowing, borrowing_id=borrowing_id)

    if request.user != borrow_req.borrower:
        messages.error(request, "Anda bukan peminjam buku ini.")
        return redirect('rak_pinjam')

    if borrow_req.status not in ['Borrowed', 'FinePending']:
        messages.error(request, "Buku tidak dalam status yang dapat di-return.")
        return redirect('rak_pinjam')

    if request.method == 'POST' and 'fine_proof' in request.FILES:
        fine_file = request.FILES.get('fine_proof')
        if not fine_file:
            messages.error(request, "Silakan unggah file bukti pembayaran denda.")
            return redirect('rak_pinjam')

        borrow_req.fine_proof = fine_file
        borrow_req.is_fine_paid = True
        borrow_req.status = 'FinePending'
        borrow_req.save(update_fields=['fine_proof', 'is_fine_paid', 'status'])

        messages.success(
            request,
            "Bukti pembayaran denda berhasil diunggah. Menunggu validasi, lalu klik Return sekali lagi."
        )
        return redirect('rak_pinjam')

    if request.method == 'POST' and 'return_action' in request.POST:
        if borrow_req.status == 'FinePending' and not borrow_req.is_fine_paid:
            messages.error(request, "Anda harus membayar denda terlebih dahulu.")
            return redirect('rak_pinjam')

        if borrow_req.status == 'FinePending' and borrow_req.is_fine_paid:
            pass
        elif borrow_req.status != 'Borrowed':
            messages.error(request, "Buku tidak dalam status ‘Borrowed’, tidak bisa di-return.")
            return redirect('rak_pinjam')

        if borrow_req.due_date is None:
            due_date = borrow_req.borrow_date + timedelta(days=7)
        else:
            due_date = borrow_req.due_date

        today = date.today()

        terlambat = (today - due_date).days
        jumlah_denda = terlambat * 3000 if terlambat > 0 else 0

        borrow_req.denda = jumlah_denda
        borrow_req.save(update_fields=['denda'])


        if jumlah_denda > 0 and not borrow_req.is_fine_paid:
            messages.error(
                request,
                f"Ada denda sebesar Rp {jumlah_denda:,}. Silakan bayar denda terlebih dahulu."
            )
            return redirect('rak_pinjam')

        borrow_req.status = 'Returned'
        borrow_req.return_date = today
        borrow_req.save(update_fields=['status', 'return_date'])

        buku = borrow_req.book
        buku.stock += 1
        buku.save()

        if jumlah_denda > 0:
            messages.success(
                request,
                f"Buku berhasil dikembalikan. Denda sebesar Rp {jumlah_denda:,} telah terbayar."
            )
        else:
            messages.success(request, "Buku berhasil dikembalikan tepat waktu. Tidak ada denda.")

        return redirect('rak_pinjam')

    return redirect('rak_pinjam')

# Review User
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def review_user_view(request, book_id):
    selected_book = get_object_or_404(booklist, book_id=book_id)
    reviewee_user = selected_book.librender
    owner_profile = Profile.objects.get(signup=reviewee_user)

    borrow_rec = borrowing.objects.filter(
        borrower=request.user,
        book=selected_book,
        status='Returned'
    ).order_by('-borrow_date').first()

    if not borrow_rec:
        messages.error(request, "Anda tidak dapat melakukan review pemilik saat ini.")
        return redirect('rak_pinjam')

    if request.method == 'POST':
        comment = request.POST.get('comment', '').strip()
        rating  = request.POST.get('rating')
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except (TypeError, ValueError):
            messages.error(request, "Rating tidak valid. Pilih angka antara 1 hingga 5 bintang.")
            return redirect('review_user', book_id=book_id)

        if not comment:
            messages.error(request, "Kolom komentar tidak boleh kosong.")
            return redirect('review_user', book_id=book_id)

        try:
            review_user.objects.create(
                reviewer=request.user,
                reviewee=reviewee_user,
                comment=comment,
                rating=rating,
            )
            messages.success(request, "Ulasan Anda untuk pemilik buku berhasil disimpan.")
        except Exception:
            messages.error(request, "Terjadi kesalahan saat menyimpan ulasan.")
            return redirect('review_user', book_id=book_id)

        borrow_rec.status = 'Finished'
        borrow_rec.save()

        return redirect('rak_pinjam')

    context = {
        'reviewee_user': reviewee_user,
        'owner_profile': owner_profile,
        'selected_book': selected_book,
        'borrow_rec': borrow_rec,
    }
    return render(request, 'libraria/review_user.html', context)

# Review Buku
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def review_book_view(request, book_id):
    selected_book = get_object_or_404(booklist, book_id=book_id)
    librarian_profile = Profile.objects.get(signup=selected_book.librender)

    borrow_rec = borrowing.objects.filter(
        borrower=request.user,
        book=selected_book,
        status='Returned'
    ).order_by('-borrow_date').first()

    if request.method == 'POST':
        comment = request.POST.get('comment', '').strip()
        rating  = request.POST.get('rating')
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except (TypeError, ValueError):
            messages.error(request, "Rating tidak valid. Pilih angka antara 1 hingga 5.")
            return redirect('review_book', book_id=book_id)

        if not comment:
            messages.error(request, "Kolom review tidak boleh kosong.")
            return redirect('review_book', book_id=book_id)

        try:
            review_book.objects.create(
                username=request.user,
                comment=comment,
                rating=rating,
                booktitle=selected_book
            )
            messages.success(request, "Terima kasih! Review buku Anda berhasil disimpan.")
        except Exception:
            messages.error(request, "Terjadi kesalahan saat menyimpan review.")
            return redirect('review_book', book_id=book_id)

        return redirect('review_user', book_id=book_id)

    context = {
        'selected_book': selected_book,
        'librarian_profile': librarian_profile,
        'borrow_rec': borrow_rec,
    }
    return render(request, 'libraria/review_book.html', context)

# Rak Pinjam
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def rak_pinjam(request):
    user_profile = Profile.objects.get(signup=request.user)
    all_borrowings = borrowing.objects.filter(borrower=request.user).order_by('-borrow_date')

    active_statuses = ['Pending', 'Borrowed', 'FinePending']
    active_borrowings = all_borrowings.filter(status__in=active_statuses)

    finished_statuses = ['Returned', 'Finished']
    finished_borrowings = all_borrowings.filter(status__in=finished_statuses)

    context = {
        'active_borrowings': active_borrowings,
        'finished_borrowings': finished_borrowings,
        'user_profile': user_profile,
    }
    return render(request, 'libraria/rak_pinjam.html', context)

#Base Dashboard
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def base_user(request):
    user_profile = Profile.objects.get(signup=request.user)
    borrowings = borrowing.objects.filter(borrower=request.user, status='Borrowed').select_related('book')
    
    context = {
        'borrowings': borrowings,
        'categories': category.objects.all(),
        'user_profile': user_profile,
        'borrowings': borrowings,
    }
    return render(request, 'libraria/base-user.html', context)

#Fitur See All
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def see_all_view(request, section):
    context = {}
    
    
    context['categories'] = category.objects.all()
    context['borrowings'] = borrowing.objects.filter(borrower=request.user, status='Borrowed').select_related('book')
    
    if section == 'book-of-the-month':
        context['section_title'] = 'Book of the Month'
        books = booklist.objects.annotate(avg_rating=Avg('review_book__rating')).order_by('-avg_rating')
        
        for book in books:
            avg = book.avg_rating or 0
            book.full_stars = range(int(round(avg)))
            book.empty_stars = range(5 - int(round(avg)))

        context['items'] = books
        context['type'] = 'book'
        
    elif section == 'recommendation':
        context['section_title'] = 'Recommendation'
        books = booklist.objects.annotate(avg_rating=Avg('review_book__rating')).filter(avg_rating__gte=3, avg_rating__lte=5).order_by('?')

        for book in books:
            avg = book.avg_rating or 0
            book.full_stars = range(int(round(avg)))
            book.empty_stars = range(5 - int(round(avg)))

        context['items'] = books
        context['type'] = 'book'

    elif section == 'librender-star':
        context['user_profile'] = Profile.objects.get(signup=request.user)
        context['section_title'] = 'Librender Star'
        profiles = Profile.objects.annotate(total_rating=Avg('signup__reviews_received__rating')).order_by('-total_rating')
        
        for profile in profiles:
            avg = profile.total_rating or 0
            profile.full_stars = range(int(round(avg)))
            profile.empty_stars = range(5 - int(round(avg)))
            
        context['items'] = profiles
        context['type'] = 'profile'

    else:
        context['section_title'] = 'Unknown Section'
        context['items'] = []
        context['type'] = 'none'

    return render(request, 'libraria/see_all.html', context)

#Cari Buku
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def search_books(request):
    borrowings = borrowing.objects.filter(borrower=request.user, status='Borrowed').select_related('book')
    categories = category.objects.all()
    query = request.GET.get('q')
    results = []

    if query:
        results = booklist.objects.filter(
            Q(title__icontains=query) | Q(category_id__category_name__icontains=query)
        ).annotate(avg_rating=Avg('review_book__rating'))

        for book in results:
            avg_rating = book.avg_rating or 0
            book.full_stars = list(range(int(avg_rating)))
            book.empty_stars = list(range(5 - int(avg_rating)))

    context = {
        'page_title': query,
        'heading': "Search Results",
        'query': query,
        'book_list': results,
        'categories': categories,
        'borrowings': borrowings,
    }
    return render(request, 'libraria/book-listing.html', context)

#Tampil Buku Berdasarkan Kategori
@login_required(login_url='login')
@allowed_users(allowed_roles=['user'])
def books_by_category(request, category_id):
    categories = category.objects.all()
    borrowings = borrowing.objects.filter(borrower=request.user, status='Borrowed').select_related('book')
    selected_category = get_object_or_404(category, category_id=category_id)

    books_in_category = booklist.objects.filter(category=selected_category).annotate(avg_rating=Avg('review_book__rating'))

    for book in books_in_category:
        avg_rating = book.avg_rating or 0
        book.full_stars = list(range(int(avg_rating)))
        book.empty_stars = list(range(5 - int(avg_rating)))

    context = {
        'page_title': selected_category.category_name,
        'heading': f"Books in {selected_category.category_name}",
        'book_list': books_in_category,
        'categories': categories,
        'borrowings': borrowings,
    }
    return render(request, 'libraria/book-listing.html', context)

# def resetPassword(request):
#     return render(request, 'libraria/resetPassword.html')

# def verificationCode(request):
#     return render(request, 'libraria/verificationCode.html')

# def newPassword(request):
#     return render(request, 'libraria/newPassword.html')