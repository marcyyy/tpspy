from django.db import models
import datetime, string, random
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save


class Tenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    unit = models.CharField(max_length=10, unique=True, blank=False)
    contact = models.CharField(max_length=15)
    work_address = models.CharField(max_length=255)
    birthday = models.DateField()

    def __str__(self):
        return self.unit


class Billing(models.Model):
    info_tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    date_issued = models.DateField(auto_now_add=True)
    BILLING_TYPE = (
        ('Association_Dues', 'Association Dues'),
        ('Water', 'Water'),
        ('Electric', 'Electric'),
        ('Cable', 'Cable'),
        ('Internet', 'Internet'),
        ('Rent', 'Rent'),
    )
    billing_type = models.CharField(max_length=20, choices=BILLING_TYPE)
    billing_fee = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    STATUS = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Processing', 'Processing')
    )
    status = models.CharField(max_length=50, choices=STATUS, default=STATUS[0][0])

    def __str__(self):
        template = '{0.info_tenant.unit} {0.due_date} {0.status} '
        return template.format(self)

    def bmonth(self):
        return self.due_date.strftime('%B')

    def byear(self):
        return self.due_date.strftime('%Y')


class Complaint(models.Model):
    info_tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    date_issued = models.DateField(auto_now_add=True)
    COMPLAINTS_NAME = (
        ('Maintenance','Maintenance Problem'),
        ('Staff','Staff Conflict'),
        ('Neighbour','Neighbor/s Issue'),
        ('Pest','Pest Invasion'),
        ('Property_Condition','Condition of Property'),
        ('Safety', 'Safety Concern'),
        ('Billing','Billing'),
        ('Others', 'Others'),
    )
    complain = models.CharField(max_length=50, choices=COMPLAINTS_NAME)
    elaborate = models.TextField(blank=True)
    neighbour = models.CharField(max_length=50, blank=True)
    staff = models.CharField(max_length=50, blank=True)
    supporting_image = models.CharField(max_length=2048, blank=True)

    def __str__(self):
        template = '{0.info_tenant.unit} {0.complain}'
        return template.format(self)

    def cmonth(self):
        return self.date_issued.strftime('%B')

    def cyear(self):
        return self.date_issued.strftime('%Y')


class Visitor(models.Model):
    info_tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    date_issued = models.DateField(auto_now_add=True)
    PURPOSE = (
        ('Vacation', 'Vacation'),
        ('One_Day', 'One Day Visit'),
        ('Overnight', 'Overnight'),
        ('Event', 'Event'),
        ('Pool_Gym', 'Use Pool/Gym')
    )
    purpose = models.CharField(max_length=50, choices=PURPOSE)
    visitor_count = models.IntegerField()
    visitor_names = models.TextField()
    visit_date = models.DateField()
    duration = models.DurationField()
    STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Declined', 'Declined'),
        ('Processing', 'Processing'),
        ('Done', 'Done')
    )
    status = models.CharField(max_length=50, choices=STATUS, default=STATUS[0][0])

    def __str__(self):
        template = '{0.info_tenant.unit} {0.visit_date} {0.status}'
        return template.format(self)

    def vmonth(self):
        return self.visitor_date.strftime('%B')

    def vyear(self):
        return self.visit_date.strftime('%Y')



