from django.db import models
from django.contrib.auth.models import User, Group


class CourseStatus(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    code = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name


class Client(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.CharField(max_length=100, blank=True, null=True)
    contact_phone = models.CharField(max_length=100, blank=True, null=True)
    users_group = models.ForeignKey(Group, on_delete=models.DO_NOTHING, default=0)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000, blank=True, null=True)
    publication_time = models.DateTimeField('date published', blank=True, null=True)
    status = models.ForeignKey(CourseStatus, on_delete=models.CASCADE, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    modified_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    created_time = models.DateTimeField('creation time', blank=True, null=True)
    last_modified_time = models.DateTimeField('last modified time', blank=True, null=True)
    cover_filename = models.CharField(max_length=1000, blank=True, null=True)

    # Property to store the current status
    is_completed = False

    def __str__(self):
        return self.name


class Catalogue(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    modified_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    created_time = models.DateTimeField('creation time', blank=True, null=True)
    last_modified_time = models.DateTimeField('last modified time', blank=True, null=True)

    def __str__(self):
        return self.name


class SlideType(models.Model):
    code = models.CharField(max_length=200, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name


class TestType(models.Model):
    code = models.CharField(max_length=200, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name


class Test(models.Model):
    type = models.ForeignKey(TestType, on_delete=models.CASCADE, blank=True, null=True)
    content = models.CharField(max_length=2000, blank=True, null=True)
    max_points = models.IntegerField(blank=True, null=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    modified_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    created_time = models.DateTimeField('creation time', blank=True, null=True)
    last_modified_time = models.DateTimeField('last modified time', blank=True, null=True)

    def __str__(self):
        return self.name


class UserTestResult(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    points = models.IntegerField(blank=True, null=True)
    last_pass_time = models.DateTimeField('last pass time', blank=True, null=True)

    def __str__(self):
        return self.name


class Slide(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    course = models.ForeignKey(SlideType, on_delete=models.CASCADE, blank=True, null=True)
    content = models.CharField(max_length=2000, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    previous_slide_id = models.IntegerField(default=0, blank=True, null=True)
    next_slide_id = models.IntegerField(default=0, blank=True, null=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    modified_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    created_time = models.DateTimeField('creation time', blank=True, null=True)
    last_modified_time = models.DateTimeField('last modified time', blank=True, null=True)
    type = models.ForeignKey(SlideType, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='+', blank=True, null=True)

    def __str__(self):
        return self.name


class UserSlideView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    slide = models.ForeignKey(Slide, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    last_view_time = models.DateTimeField('last viewed date', blank=True, null=True)


class Catalogue(models.Model):
    name = models.CharField(max_length=1000, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    modified_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    created_time = models.DateTimeField('creation time', blank=True, null=True)
    last_modified_time = models.DateTimeField('last modified time', blank=True, null=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=1000, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    catalogue = models.ForeignKey(Catalogue, on_delete=models.CASCADE, blank=True, null=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    modified_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    created_time = models.DateTimeField('creation time', blank=True, null=True)
    last_modified_time = models.DateTimeField('last modified time', blank=True, null=True)

    def __str__(self):
        return self.name


class ItemProperty(models.Model):
    name = models.CharField(max_length=1000, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    catalogue = models.ForeignKey(Catalogue, on_delete=models.CASCADE, blank=True, null=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    modified_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    created_time = models.DateTimeField('creation time', blank=True, null=True)
    last_modified_time = models.DateTimeField('last modified time', blank=True, null=True)

    def __str__(self):
        return self.name


class ItemPropertyValue(models.Model):
    item_property = models.ForeignKey(ItemProperty, on_delete=models.CASCADE, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)
    value = models.CharField(max_length=1000, blank=True, null=True)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    modified_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    created_time = models.DateTimeField('creation time', blank=True, null=True)
    last_modified_time = models.DateTimeField('last modified time', blank=True, null=True)

    def __str__(self):
        return self.name


class UserCourseStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    course_is_in_progress = models.BooleanField()
    course_is_completed = models.BooleanField()
    updated_time = models.DateTimeField('updated time', blank=True, null=True)
