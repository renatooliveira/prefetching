from django.db import models


class Owner(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    pizzas = models.ManyToManyField('Pizza', blank=True, related_name='restaurants')
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='restaurants')

    def __str__(self):
        return self.name


class Pizza(models.Model):
    name = models.CharField(max_length=200)
    toppings = models.ManyToManyField('Topping', blank=True, related_name='pizzas')
    is_vegetarian = models.BooleanField(default=False)

    def __str__(self):
        return self.name



class Topping(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name