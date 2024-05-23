from django.test import TestCase
from django.db.models import Prefetch

from pizzas.models import Owner, Restaurant, Pizza, Topping


class TestQueryCount(TestCase):

    def setUp(self) -> None:

        self.owner1 = Owner.objects.create(name='Owner 1')
        self.owner2 = Owner.objects.create(name='Owner 2')
        self.topping1 = Topping.objects.create(name='Cheese')
        self.topping2 = Topping.objects.create(name='Pepperoni')
        self.topping3 = Topping.objects.create(name='Mushrooms')
        self.pizza1 = Pizza.objects.create(name='Pepperoni Pizza')
        self.pizza1.toppings.add(self.topping1, self.topping2)
        self.pizza2 = Pizza.objects.create(name='Cheese Pizza')
        self.pizza2.toppings.add(self.topping1)
        self.pizza3 = Pizza.objects.create(name='Mushroom Pizza', is_vegetarian=True)
        self.pizza3.toppings.add(self.topping3)
        self.restaurant1 = Restaurant.objects.create(name='Restaurant 1', owner=self.owner1)
        self.restaurant1.pizzas.add(self.pizza1, self.pizza2)
        self.restaurant2 = Restaurant.objects.create(name='Restaurant 2', owner=self.owner2)
        self.restaurant2.pizzas.add(self.pizza2, self.pizza3)
        self.restaurant3 = Restaurant.objects.create(name='Restaurant 2', owner=self.owner2)
        self.restaurant3.pizzas.add(self.pizza1, self.pizza3)

        return super().setUp()
    
    def test_when_queries_are_evaluated(self):
        print('>>> When queries are evaluated')
        with self.assertNumQueries(0):
            restaurants = Restaurant.objects.all()
        
        with self.assertNumQueries(0):
            restaurants = Restaurant.objects.all()[1:10]
        
        with self.assertNumQueries(1):
            restaurants = list(Restaurant.objects.all())
    
    def test_n_plus_one_problem(self):
        print('>>> N+1 problem')
        with self.assertNumQueries(4):
            restaurants = Restaurant.objects.all()
            for restaurant in restaurants:
                print(restaurant.owner.name)
        
    def test_restaurant_owner_query_count(self):
        print('>>> Restaurant owner query count')

        with self.assertNumQueries(4):
            restaurants = Restaurant.objects.all()
            for restaurant in restaurants:
                print(restaurant.owner.name)

        with self.assertNumQueries(1):
            restaurants = Restaurant.objects.select_related('owner')
            for restaurant in restaurants:
                print(restaurant.owner.name)

    def test_restaurant_pizzas_query_count(self):
        print('>>> Restaurant pizzas query count')
            
        with self.assertNumQueries(4):
            restaurants = Restaurant.objects.all()
            for restaurant in restaurants:
                print(restaurant.pizzas.all())

        with self.assertNumQueries(2):
            restaurants = Restaurant.objects.prefetch_related('pizzas')
            for restaurant in restaurants:
                print(restaurant.pizzas.all())
    
    def test_restaurant_pizza_toppings_query_count(self):
        print('>>> Restaurant pizza toppings query count')
            
        with self.assertNumQueries(10):
            restaurants = Restaurant.objects.all()
            for restaurant in restaurants:
                for pizza in restaurant.pizzas.all():
                    print(pizza.toppings.all())

        with self.assertNumQueries(3):
            restaurants = Restaurant.objects.prefetch_related('pizzas__toppings')
            print(restaurants.query)
            for restaurant in restaurants:
                for pizza in restaurant.pizzas.all():
                    print(pizza.toppings.all())
    
    def test_prefetch_class(self):
        print('>>> Prefetch class')
        with self.assertNumQueries(2):
            restaurants = Restaurant.objects.prefetch_related(Prefetch("pizzas", queryset=Pizza.objects.order_by('-name')))
            for restaurant in restaurants:
                print(restaurant.pizzas.all())
    
    def test_prefetch_class_to_attr(self):
        print('>>> Prefetch class to_attr')
        with self.assertNumQueries(3):
            restaurants = Restaurant.objects.prefetch_related(
                Prefetch("pizzas", queryset=Pizza.objects.filter(is_vegetarian=True), to_attr='vegetarian_pizzas'),
                "vegetarian_pizzas__toppings")
            for restaurant in restaurants:
                print(restaurant.vegetarian_pizzas)
                for pizza in restaurant.vegetarian_pizzas:
                    print(pizza.toppings.all())
