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
        
        if role != "admin":
            user_profile = UserProfile(
                user = user,
                password = password
            )
            user_profile.save()
            

        return user

    def create_superuser(self, first_name, middle_name, last_name, email, phone_number,gender,role, password):
        user = self.create_user(first_name, middle_name, last_name, email, gender, phone_number,role,password)
        user.is_staff = True
        user.is_superuser = True
        user.role = "admin"
        user.save(using=self._db)
        user_profile = UserProfile(
            user = user
        )
        user_profile.save()
            
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
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'middle_name', 'last_name', 'gender', 'phone_number', 'role']
    
    def save(self, *args, **kwargs):
        base_username = f"{self.first_name}{self.middle_name}{self.last_name}".lower()
        similar_users = CustomUser.objects.filter(username__startswith=base_username).exclude(pk=self.pk).count()

        if similar_users > 0:
            self.username = f"{base_username}-{similar_users + 1}"
        else:
            self.username = base_username

        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    username = models.CharField(max_length=150, blank=True, null=True)
    user_pic = models.ImageField(upload_to="avatars", blank=True, null=True)
    password = models.CharField(max_length=150, blank=True, null=True)
    def save(self, *args, **kwargs):
        if self.user:
            self.username = f"{self.user.first_name} {self.user.middle_name}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username}"

class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender} to {self.receiver} at {self.timestamp}"


class Subject(models.Model):
    subject_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.subject_name}" 

class Class(models.Model):
    class_name = models.CharField(max_length=50, unique=True, primary_key=True)
    
    def __str__(self):
        return self.class_name

    def clean(self):
        if self.class_name:
            self.class_name = self.class_name.upper()
            
class ClassSubject(models.Model):
    class_room = models.ForeignKey("ClassRoom", on_delete=models.PROTECT, related_name="class_subjects")
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="subject_classes")
    teacher = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name="teaching_subjects", limit_choices_to={'role': 'teacher'})

    class Meta:
        unique_together = ('class_room', 'subject')  # ✅ Only one teacher per subject in a class


    def __str__(self):
        return f"{self.subject} in {self.class_room} by {self.teacher.username}"


class ClassRoom(models.Model):
    class_name = models.OneToOneField(Class, on_delete=models.PROTECT, related_name="classroom_set")
    room_teacher = models.OneToOneField(CustomUser, on_delete=models.PROTECT, null=True, limit_choices_to={'role': 'teacher'})
    students = models.ManyToManyField(CustomUser, related_name='classroom_students', limit_choices_to={'role': 'student'})
    def __str__(self):
        return f"{self.class_name}--{self.room_teacher}"


class Activity(models.Model):
    """
    One scored activity (test/quiz/homework) in a class & subject.
    """
    class_room    = models.ForeignKey(
        ClassRoom,
        on_delete=models.PROTECT,
        related_name="activities",
    )
    subject       = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="activities",
    )
    teacher       = models.ForeignKey(
        UserProfile,
        on_delete=models.PROTECT,
        related_name="activities_created",
    )
    activity_type = models.CharField(
        max_length=20,
        choices=[
            ("test","Test"), 
            ("quiz","Quiz"), 
            ("homework","Homework")
        ],
    )
    activity_name = models.CharField(max_length=100)
    date_created  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("class_room","subject","activity_name")
        ordering        = ["-date_created"]

    def __str__(self):
        return f"{self.get_activity_type_display()}: {self.activity_name}"


class Mark(models.Model):
    """
    A single student's score on one Activity.
    """
    activity  = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="marks",
    )
    student   = models.ForeignKey(
        UserProfile,
        on_delete=models.PROTECT,
        related_name="marks_received",
    )
    score     = models.DecimalField(max_digits=5, decimal_places=2)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("activity","student")
        ordering        = ["activity","student"]

    def __str__(self):
        return f"{self.student} → {self.score} on {self.activity}"