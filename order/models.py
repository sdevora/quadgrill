import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField

from core.utils import shorten_url


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    cc_number = models.CharField(max_length=20, null=True, blank=True)
    phone = PhoneNumberField()

    @property
    def full_name(self):
        return u'{} {}'.format(self.first_name, self.last_name)

    def __unicode__(self):
        return self.full_name


class OrderItem(models.Model):
    item = models.ForeignKey('menu.Item')
    order = models.ForeignKey('order.Order')
    quantity = models.IntegerField(default=1)

    def __unicode__(self):
        return u'{} {}'.format(self.quantity, self.item.name)


class Order(models.Model):

    PAYMENT_CHOICES = [
        ('Crimson Cash', 'Crimson Cash',),
        ('Board Plus', 'Board Plus',),
        ('Cash', 'Cash',),
    ]

    payment_type = models.CharField(max_length=100, choices=PAYMENT_CHOICES, default='Crimson Cash')
    time = models.DateTimeField(auto_now=True)
    tip = models.DecimalField(max_digits=6, decimal_places=2)
    customer = models.ForeignKey(Customer)
    accepted = models.BooleanField(default=False)
    time_accepted = models.DateTimeField(null=True, blank=True)
    time_estimate = models.IntegerField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)
    time_completed = models.DateTimeField(null=True, blank=True)
    key = models.CharField(max_length=64, null=True, blank=True)
    cancellation_reason = models.CharField(max_length=500, null=True, blank=True)

    def add_item(self, item, quantity=1):
        try:
            current_item = self.orderitem_set.get(item=item)
            current_item.quantity += quantity
            current_item.save()
        except ObjectDoesNotExist:
            OrderItem.objects.create(item=item, quantity=quantity, order=self)

    @property
    def status(self):
        if self.completed:
            return 'Complete'
        elif self.accepted and self.canceled:
            return 'Canceled'
        elif self.canceled:
            return 'Declined'
        elif self.accepted:
            return 'In Progress'
        else:
            return 'In Queue'

    @property
    def total(self):
        total = self.tip
        for order_item in self.orderitem_set.all():
            total += order_item.quantity * order_item.item.price
        return total

    @property
    def eta(self):
        if self.time_estimate and not self.canceled:
            return self.time_accepted + datetime.timedelta(seconds=60 * self.time_estimate)
        return None

    @property
    def time_to_complete(self):
        delta = (self.time_completed - self.time_accepted)
        seconds = float(delta.seconds)
        minutes = round(seconds/60, 0)
        return '{} minutes'.format(int(minutes))

    @property
    def number(self):
        return self.pk

    @property
    def payment_type_display(self):
        payment_type = self.payment_type
        if payment_type == 'Crimson Cash':
            return u'{} ({})'.format(payment_type, self.customer.cc_number)
        else:
            return payment_type


    def get_short_tracking_url(self):
        return shorten_url('order:track', key=self.key)


    def __unicode__(self):
        return u"{}'s order for ${} at {}".format(
            self.customer.full_name,
            self.total,
            self.time,
        )
