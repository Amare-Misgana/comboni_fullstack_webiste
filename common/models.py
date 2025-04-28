from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager



class CustomUserManager(BaseUserManager):
    def create_user(self, first_name, middle_name, last_name, email, gender, phone_number, role, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            email=self.normalize_email(email),
            gender=gender,
            phone_number=phone_number,
            role=role,
        )

        # Generate base username from the first, middle, and last names
        base_username = f"{first_name}{middle_name}{last_name}".lower()
        
        # Check if the base username already exists
        similar_users = CustomUser.objects.filter(username__startswith=base_username).count()
        
        if similar_users > 0:
            user.username = f"{base_username}-{similar_users + 1}"
        else:
            user.username = base_username

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, middle_name, last_name, email, gender, phone_number, role, password):
        user = self.create_user(first_name, middle_name, last_name, email, gender, phone_number, role, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )

    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'middle_name', 'last_name', 'gender', 'phone_number', 'role']

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    username = models.CharField(max_length=150)
    user_pic = models.ImageField(upload_to="avatars")
    def save(self, *args, **kwargs):
        if self.user:
            self.username = f"{self.user.first_name} {self.user.middle_name}"
        super().save(*args, **kwargs)

class Message(models.Model):
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender} to {self.receiver} at {self.timestamp}"