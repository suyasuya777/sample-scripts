from roboter.models import ranking
from roboter.views import console


class RestaurantRobot:
    def __init__(self, name="Robo", user_name=""):
        self.name = name
        self.user_name = user_name
        self.ranking_model = ranking.RankingModel()

    def hello(self):
        template = console.get_template("hello.txt")
        while True:
            user_name = input(template.substitute(robot_name=self.name))
            if user_name:
                self.user_name = user_name
                break

    def recomend_restaurant(self):
        new_recoment_restaurant = self.ranking_model.get_most_popular()
        if not new_recoment_restaurant:
            return None

        will_recoment_restaurants = [new_recoment_restaurant]

        while True:
            template = console.get_template("greeting.txt")
            is_yes = input(template.substitute(restaurant=new_recoment_restaurant))

            if is_yes == "y":
                break

            if is_yes == "n":
                new_recoment_restaurant = self.ranking_model.get_most_popular(
                    will_recoment_restaurants
                )
                if not new_recoment_restaurant:
                    break
                will_recoment_restaurants.append(new_recoment_restaurant)

    def ask_user_favorite(self):
        while True:
            template = console.get_template("which_restaurant.txt")
            restaurant = input(template.substitute(user_name=self.user_name))
            if restaurant:
                self.ranking_model.increment(restaurant)
                break

    def thank_you(self):
        template = console.get_template("good_by.txt")
        print(template.substitute(robot_name=self.name, user_name=self.user_name))
