from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

# Create your models here.
class Profile(models.Model):
    signup = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    user_id = models.CharField(
        max_length=5,
        primary_key=True,
    )
    name = models.CharField(max_length=50)
    bio = models.CharField(max_length=20)
    profile_picture = models.ImageField(upload_to='profile_pic/', blank=True, null=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    account = models.CharField(max_length=20) 

    def save(self, *args, **kwargs):
        if not self.user_id:
            last_user = Profile.objects.all().order_by('user_id').last()
            
            if last_user:
                last_id = int(last_user.user_id[1:])
                new_id = last_id + 1
            else:
                new_id = 1

            self.user_id = f"R{new_id:04d}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.user_id

# Review Web
class ReviewWeb(models.Model):
    revw_id = models.CharField(
        max_length=5,
        primary_key=True,
    )
    review_field = models.TextField()

    def save(self, *args, **kwargs):
        if not self.revw_id:
            last_user = ReviewWeb.objects.all().order_by('revw_id').last()
            
            if last_user and last_user.revw_id:
                try:
                    last_id = int(last_user.revw_id[2:])
                    new_id = last_id + 1
                except ValueError:
                    new_id = 1
            else:
                new_id = 1

            self.revw_id = f"RW{new_id:03d}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.revw_id

# Category
class category(models.Model):
    category_id = models.CharField(
        max_length=5,
        primary_key=True,
        null=False, 
        blank=False
    ) 
    
    category_name = models.CharField(max_length=20, null=False, blank=False)
    desc = models.TextField(null=False, blank=False)
    
    
    def save(self, *args, **kwargs):
        if not self.category_id:
            last_category = category.objects.all().order_by('category_id').last()
            
            if last_category:
                last_id = int(last_category.category_id[1:])
                new_id = last_id +1
            else:
                new_id = 1

            self.category_id = f"C{new_id:04d}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.category_name

# Book List
class booklist(models.Model):
    book_id = models.CharField(
        max_length=5,
        primary_key=True,
        null=False,
        blank=False,
        unique=True
    )

    title = models.CharField(max_length=150)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=150)
    number_of_pages = models.PositiveIntegerField()
    years = models.PositiveBigIntegerField()
    category = models.ForeignKey(category, on_delete=models.CASCADE)
    synopsis = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cover_image = models.ImageField(upload_to='cover/')
    stock = models.PositiveIntegerField()

    librender = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.book_id:  
            last_book = booklist.objects.all().order_by('book_id').last()
            if last_book:
                last_id = int(last_book.book_id[1:])
                new_id = last_id + 1
            else:
                new_id = 1
            self.book_id = f"B{new_id:04d}"

        super().save(*args, **kwargs)

    def _str_(self):
        return self.book_id

# Review User
class review_user(models.Model):
    reviewuser_id = models.CharField(
        max_length=5,
        primary_key=True,
        null=False, 
        blank=False
    )
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    comment = models.TextField(null=False, blank=False)
    rating = models.PositiveSmallIntegerField(null=False, blank=False)
    
    def save(self, *args, **kwargs):
        if not self.reviewuser_id:
            last_reviewuser = review_user.objects.all().order_by('reviewuser_id').last()
            
            if last_reviewuser:
                last_id = int(last_reviewuser.reviewuser_id[2:])
                new_id = last_id +1
            else:
                new_id = 1

            self.reviewuser_id = f"RU{new_id:03d}"
        
        super().save(*args, **kwargs)
    
    def _str_(self):
        return self.reviewuser_id

# Borrowing
def default_return_date():
    return timezone.now().date() + timedelta(days=7)

class borrowing(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Borrowed', 'Borrowed'),
        ('Returned', 'Returned'),
        ('Declined', 'Declined'),
        ('Finished', 'Finished'),
        ('FinePending', 'Fine Pending'),
    ]

    borrowing_id = models.CharField(max_length=5, primary_key=True)
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="borrowed_by")
    book = models.ForeignKey('booklist', on_delete=models.CASCADE, related_name="borrowed_books")
    borrow_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(default=default_return_date)
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    denda = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    payment_proof = models.ImageField(upload_to='payment_proofs/', null=True, blank=True)
    fine_proof = models.ImageField(upload_to='bukti_denda/', null=True, blank=True)
    is_fine_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.borrowing_id:
            last_borrowing = borrowing.objects.all().order_by('borrowing_id').last()
            if last_borrowing:
                last_id = int(last_borrowing.borrowing_id[1:])
                new_id = last_id + 1
            else:
                new_id = 1
            self.borrowing_id = f"P{new_id:04d}"
        super(borrowing, self).save(*args, **kwargs)

    def __str__(self):
        return self.borrowing_id
    
class review_book(models.Model):
    reviewbook_id = models.CharField(
        max_length=5,
        primary_key=True,
        null=False, 
        blank=False
    )
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    
    comment = models.TextField(null=False, blank=False)
    rating = models.PositiveSmallIntegerField(null=False, blank=False)
    booktitle = models.ForeignKey(booklist, on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        if not self.reviewbook_id:
            last_reviewbook = review_book.objects.all().order_by('reviewbook_id').last()
            
            if last_reviewbook:
                last_id = int(last_reviewbook.reviewbook_id[2:])
                new_id = last_id +1
            else:
                new_id = 1

            self.reviewbook_id = f"RB{new_id:03d}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.reviewbook_id