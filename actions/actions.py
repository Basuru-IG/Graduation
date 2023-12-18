from typing import Any, Text, Dict, List
import pymongo
from math import radians, sin, cos, sqrt, atan2
import googlemaps
import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import random
from rasa_sdk.events import SlotSet

import pymongo
from math import radians, sin, cos, sqrt, atan2
import googlemaps
import requests
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Graduation_project"]
district_collection = db["District"]
restaurant_collection = db["Restaurant"]

DATABASE = ["bún đậu mắm tôm",
            "bún đậu nước mắm",
            "bún cá",
            "bún hải sản",
            "cơm văn phòng",
            "cơm sườn",
            "xôi",
            "bún ốc",
            "mì vằn thắn",
            "hủ tiếu",
            "bún chả",
            "bún ngan",
            "ngan xào tỏi",
            "bún bò huế",
            "mì tôm hải sản",
            "bánh mì trứng xúc xích rắc thêm ít ngải cứu",
            "bánh mì trứng",
            "bánh mì xúc xích",
            "bánh mì pate", 
            "phở"]


class ActionRecommend(Action):

    def name(self) -> Text:
        return "action_recommend"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("run action restaurant commend")
        food = []
        for i in range(2):
            food_number = random.randrange(len(DATABASE))
            food.append(DATABASE[food_number])

        dispatcher.utter_message(
            text="Em nghĩ hôm nay anh chị có thể thử món '{}' hoặc bên cạnh đó cũng có thể là món '{}' ạ".format(food[0], food[1]))

        return []
    
# class ActionGetLocation(Action):
#     def name(self) -> Text:
#         return "action_get_location"

#     async def run(
#         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
#     ) -> List[Dict[Text, Any]]:
#         message = tracker.latest_message
#         location = message.get("location")
#         if location:
#             dispatcher.utter_message(text=f"Thanks for sharing your location: {location}")
#         else:
#             dispatcher.utter_message(text="Sorry, I didn't get your location.")
#         return []


def get_coordinates(address):
    address=address+" Thanh Pho Ho Chi Minh"
    api_key = ''  # Replace with your API key
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}'
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        # Extract latitude and longitude from the API response
        data = response.json()['results'][0]['geometry']['location']
        lat, lng = data['lat'], data['lng']
        return lat, lng
        # return 10.787698, 106.697676
    else:
        print('Error:', response.status_code)

EARTH_RADIUS_KM = 6371

def distance(point1, point2):
    lat1, lon1 = point1['Latitude'], point1['Longitude']
    lat2, lon2 = point2['Latitude'], point2['Longitude']
    R = 6371  # earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return EARTH_RADIUS_KM * c
def get_restaurant_near_by(user_address, address, cuisine):
    # print("user   "+user_address)
    # print("address   "+address)
    # PendingDeprecationWarning
    if user_address and address:
        if "Quận" in address:
            documents = district_collection.find({"name": address})
            near_by_list = documents[0]["NearBy"]
            restaurant_list = restaurant_collection.find({"DistrictId": {"$in": near_by_list}})
            count = 1
            data = []
            for restaurant in restaurant_list:
                data.append(restaurant)
                count = count +1
            lat, lng = get_coordinates(user_address)
            print(f'Latitude: {lat}, Longitude: {lng}')
            point = {'Longitude': lng, 'Latitude': lat}
            sorted_locations = sorted(filter(lambda loc: distance(point, loc) < 3, data), key=lambda loc: distance(point, loc))
            # selected_locations = random.sample(sorted_locations, 10)
            selected_locations = sorted_locations
        else:
            words = address.split()
            if "đường" in words:
                words.remove("đường")
                address = " ".join(words)
            print(address)
            restaurant_list = restaurant_collection.find({"Address": {"$regex": address, "$options": "i"}})
            count = 1
            data = []
            for restaurant in restaurant_list:
                data.append(restaurant)
                count = count +1 
            lat, lng = get_coordinates(user_address)
            print(f'Latitude: {lat}, Longitude: {lng}')
            point = {'Longitude': lng, 'Latitude': lat}
            sorted_locations = sorted(filter(lambda loc: distance(point, loc) < 3, data), key=lambda loc: distance(point, loc))
            # selected_locations = random.sample(sorted_locations, 10)
            selected_locations = sorted_locations
    elif address is None and user_address:
        if "Quận" in user_address:
            documents = district_collection.find({"name": user_address})
            near_by_list = documents[0]["NearBy"]
            restaurant_list = restaurant_collection.find({"DistrictId": {"$in": near_by_list}})
            count = 1
            data = []
            for restaurant in restaurant_list:
                data.append(restaurant)
                count = count +1 
            print(count)
            lat, lng = get_coordinates(user_address)
            print(f'Latitude: {lat}, Longitude: {lng}')
            point = {'Longitude': lng, 'Latitude': lat}
            sorted_locations = sorted(filter(lambda loc: distance(point, loc) < 3, data), key=lambda loc: distance(point, loc))
            # selected_locations = random.sample(sorted_locations, 10)
            selected_locations = sorted_locations
        else:
            words = user_address.split()
            if "đường" in words:
                words.remove("đường")
                user_address = " ".join(words)
            print(user_address)
            restaurant_list = restaurant_collection.find({"Address": {"$regex": user_address, "$options": "i"}})
            count = 1
            data = []
            for restaurant in restaurant_list:
                data.append(restaurant)
                count = count +1 
            print(count)
            lat, lng = get_coordinates(user_address)
            print(f'Latitude: {lat}, Longitude: {lng}')
            point = {'Longitude': lng, 'Latitude': lat}
            sorted_locations = sorted(filter(lambda loc: distance(point, loc) < 3, data), key=lambda loc: distance(point, loc))
            # selected_locations = random.sample(sorted_locations, 10)
            selected_locations = sorted_locations
    elif user_address is None and address:
        if "Quận" in address:
            documents = district_collection.find({"name": address})
            near_by_list = documents[0]["NearBy"]
            restaurant_list = restaurant_collection.find({"DistrictId": {"$in": near_by_list}})
            count = 1
            data = []
            for restaurant in restaurant_list:
                data.append(restaurant)
                count = count +1 
            print(count)
            lat, lng = get_coordinates(address)
            print(f'Latitude: {lat}, Longitude: {lng}')
            point = {'Longitude': lng, 'Latitude': lat}
            sorted_locations = sorted(filter(lambda loc: distance(point, loc) < 3, data), key=lambda loc: distance(point, loc))
            # selected_locations = random.sample(sorted_locations, 10)
            selected_locations = sorted_locations
        else:
            words = address.split()
            if "đường" in words:
                words.remove("đường")
                address = " ".join(words)
            print(address)
            restaurant_list = restaurant_collection.find({"Address": {"$regex": address, "$options": "i"}})
            count = 1
            data = []
            for restaurant in restaurant_list:
                data.append(restaurant)
                count = count +1 
            print(count)
            lat, lng = get_coordinates(address)
            print(f'Latitude: {lat}, Longitude: {lng}')
            point = {'Longitude': lng, 'Latitude': lat}
            sorted_locations = sorted(filter(lambda loc: distance(point, loc) < 3, data), key=lambda loc: distance(point, loc))
            # selected_locations = random.sample(sorted_locations, 10)
            selected_locations = sorted_locations
    elif user_address is None and address is None:
            if cuisine is None:
                top_10_restaurants = restaurant_collection.find().sort([("TotalReview", -1), ("AvgRatingOriginal", -1)]).limit(100)
                data = []
                for restaurant in top_10_restaurants:
                    data.append(restaurant)
                    # print(f"{restaurant['Name']}: TotalReview = {restaurant['TotalReview']}, AvgRatingOriginal = {restaurant['AvgRatingOriginal']}")
                # selected_locations = random.sample(data, 10)
                selected_locations = data
            else:
                top_10_restaurants = restaurant_collection.find({
                    "$or":[
                        {"Cuisines.Name": {"$regex": cuisine, "$options": "i"}},
                        {"Name": {"$regex": cuisine, "$options": "i"}}
                    ]
                }).sort([("TotalReview", -1), ("AvgRatingOriginal", -1)]).limit(10)
                data = []
                for restaurant in top_10_restaurants:
                    data.append(restaurant)
                    # print(restaurant)
                    # print(f"{restaurant['Name']}: TotalReview = {restaurant['TotalReview']}, AvgRatingOriginal = {restaurant['AvgRatingOriginal']}")
                # selected_locations = random.sample(data, 10)
                selected_locations = data
    if cuisine is None:
        return random.sample(selected_locations, 10)
    else:
        return_data = []
        for location in selected_locations:
            # print(location)
            if cuisine.lower() in location["Name"].lower() or is_cuisine_in_location(cuisine, location):
                return_data.append(location)
        if len(return_data) >= 10:
            return random.sample(return_data, 10)
        else:
            return return_data
def get_restaurant_high_rate(user_address, address, cuisine):
    # print("user   "+user_address)
    if user_address and address:
        if "Quận" in address:
            documents = district_collection.find({"name": address})
            near_by_list = documents[0]["NearBy"]
            restaurant_list = restaurant_collection.find({"DistrictId": {"$in": near_by_list}})
            count = 1
            data = []
            for restaurant in restaurant_list:
                data.append(restaurant)
                count = count +1
            lat, lng = get_coordinates(user_address)
            print(f'Latitude: {lat}, Longitude: {lng}')
            point = {'Longitude': lng, 'Latitude': lat}
            sorted_locations = sorted(filter(lambda loc: distance(point, loc) < 3, data), key=lambda loc: distance(point, loc))
            # selected_locations = random.sample(sorted_locations, 10)
            selected_locations = sorted_locations
        else:
            words = address.split()
            if "đường" in words:
                words.remove("đường")
                address = " ".join(words)
            print(address)
            restaurant_list = restaurant_collection.find({"Address": {"$regex": address, "$options": "i"}})
            count = 1
            data = []
            for restaurant in restaurant_list:
                data.append(restaurant)
                count = count +1 
            lat, lng = get_coordinates(user_address)
            print(f'Latitude: {lat}, Longitude: {lng}')
            point = {'Longitude': lng, 'Latitude': lat}
            sorted_locations = sorted(filter(lambda loc: distance(point, loc) < 3, data), key=lambda loc: distance(point, loc))
            # selected_locations = random.sample(sorted_locations, 10)
            selected_locations = sorted_locations
    elif address is None and user_address:
        if "Quận" in user_address:
            documents = district_collection.find({"name": user_address})
            near_by_list = documents[0]["NearBy"]
            restaurant_list = restaurant_collection.find({"DistrictId": {"$in": near_by_list}})
            count = 1
            data = []
            for restaurant in restaurant_list:
                data.append(restaurant)
                count = count +1 
            print(count)
            lat, lng = get_coordinates(user_address)
            print(f'Latitude: {lat}, Longitude: {lng}')
            point = {'Longitude': lng, 'Latitude': lat}
            sorted_locations = sorted(filter(lambda loc: distance(point, loc) < 3, data), key=lambda loc: distance(point, loc))
            # selected_locations = random.sample(sorted_locations, 10)
            selected_locations = sorted_locations
        else:
            words = user_address.split()
            if "đường" in words:
                words.remove("đường")
                user_address = " ".join(words)
            print(user_address)
            restaurant_list = restaurant_collection.find({"Address": {"$regex": user_address, "$options": "i"}})
            count = 1
            data = []
            for restaurant in restaurant_list:
                data.append(restaurant)
                count = count +1 
            print(count)
            lat, lng = get_coordinates(user_address)
            print(f'Latitude: {lat}, Longitude: {lng}')
            point = {'Longitude': lng, 'Latitude': lat}
            sorted_locations = sorted(filter(lambda loc: distance(point, loc) < 3, data), key=lambda loc: distance(point, loc))
            # selected_locations = random.sample(sorted_locations, 10)
            selected_locations = sorted_locations
    elif user_address is None and address:
        if "Quận" in address:
            documents = district_collection.find({"name": address})
            near_by_list = documents[0]["NearBy"]
            restaurant_list = restaurant_collection.find({"DistrictId": {"$in": near_by_list}})
            count = 1
            data = []
            for restaurant in restaurant_list:
                data.append(restaurant)
                count = count +1 
            print(count)
            lat, lng = get_coordinates(address)
            print(f'Latitude: {lat}, Longitude: {lng}')
            point = {'Longitude': lng, 'Latitude': lat}
            sorted_locations = sorted(filter(lambda loc: distance(point, loc) < 3, data), key=lambda loc: distance(point, loc))
            # selected_locations = random.sample(sorted_locations, 10)
            selected_locations = sorted_locations
        else:
            words = address.split()
            if "đường" in words:
                words.remove("đường")
                address = " ".join(words)
            print(address)
            restaurant_list = restaurant_collection.find({"Address": {"$regex": address, "$options": "i"}})
            count = 1
            data = []
            for restaurant in restaurant_list:
                data.append(restaurant)
                count = count +1 
            print(count)
            lat, lng = get_coordinates(address)
            print(f'Latitude: {lat}, Longitude: {lng}')
            point = {'Longitude': lng, 'Latitude': lat}
            sorted_locations = sorted(filter(lambda loc: distance(point, loc) < 3, data), key=lambda loc: distance(point, loc))
            # selected_locations = random.sample(sorted_locations, 10)
            selected_locations = sorted_locations
    elif user_address is None and address is None:
            if cuisine is None:
                top_10_restaurants = restaurant_collection.find().sort([("TotalReview", -1), ("AvgRatingOriginal", -1)]).limit(100)
                data = []
                for restaurant in top_10_restaurants:
                    data.append(restaurant)
                    # print(f"{restaurant['Name']}: TotalReview = {restaurant['TotalReview']}, AvgRatingOriginal = {restaurant['AvgRatingOriginal']}")
                # selected_locations = random.sample(data, 10)
                selected_locations = data
            else:
                top_10_restaurants = restaurant_collection.find({
                    "$or":[
                        {"Cuisines.Name": {"$regex": cuisine, "$options": "i"}},
                        {"Name": {"$regex": cuisine, "$options": "i"}}
                    ]
                }).sort([("TotalReview", -1), ("AvgRatingOriginal", -1)]).limit(10)
                data = []
                for restaurant in top_10_restaurants:
                    data.append(restaurant)
                    # print(restaurant)
                    # print(f"{restaurant['Name']}: TotalReview = {restaurant['TotalReview']}, AvgRatingOriginal = {restaurant['AvgRatingOriginal']}")
                # selected_locations = random.sample(data, 10)
                selected_locations = data
    filtered_restaurants = [r for r in selected_locations if r['AvgRatingOriginal'] > 7.5]
    if cuisine is None:
        return random.sample(filtered_restaurants, 10)
    else:
        return_data = []
        for location in filtered_restaurants:
            if cuisine.lower() in location["Name"].lower() or is_cuisine_in_location(cuisine, location):
                return_data.append(location)
        if len(return_data) >= 10:
            return random.sample(return_data, 10)
        else:
            return return_data

def is_cuisine_in_location(cuisine, location):
    cuisines = location["Cuisines"]
    for c in cuisines:
        if cuisine.lower() in c["Name"].lower():
            return True
    return False

def get_restaurant(user_address, address, cuisine):
    # print("user   "+user_address)
    # print("address   "+address
    if user_address and address:
        print(1)
        if "Quận" in address:
            restaurant_list = restaurant_collection.find({"District": address})
            count = 1
            data = []
            for restaurant in restaurant_list:
                data.append(restaurant)
                count = count +1
            lat, lng = get_coordinates(user_address)
            print(f'Latitude: {lat}, Longitude: {lng}')
            point = {'Longitude': lng, 'Latitude': lat}
            sorted_locations = sorted(filter(lambda loc: distance(point, loc) < 3, data), key=lambda loc: distance(point, loc))
            # selected_locations = random.sample(sorted_locations, 10)
            # return selected_locations
            selected_locations = sorted_locations
        else:
            words = address.split()
            if "đường" in words:
                words.remove("đường")
                address = " ".join(words)
            print(address)
            restaurant_list = restaurant_collection.find({"Address": {"$regex": address, "$options": "i"}})
            count = 1
            data = []
            for restaurant in restaurant_list:
                data.append(restaurant)
                count = count +1 
            lat, lng = get_coordinates(user_address)
            print(f'Latitude: {lat}, Longitude: {lng}')
            point = {'Longitude': lng, 'Latitude': lat}
            sorted_locations = sorted(filter(lambda loc: distance(point, loc) < 3, data), key=lambda loc: distance(point, loc))
            # selected_locations = random.sample(sorted_locations, 10)
            # return selected_locations
            selected_locations = sorted_locations
    elif address is None and user_address:
        print(2)
        if "Quận" in user_address:
            restaurant_list = restaurant_collection.find({"District": user_address})
            count = 1
            data = []
            for restaurant in restaurant_list:
                data.append(restaurant)
                count = count +1 
            print(count)
            lat, lng = get_coordinates(user_address)
            print(f'Latitude: {lat}, Longitude: {lng}')
            point = {'Longitude': lng, 'Latitude': lat}
            sorted_locations = sorted(filter(lambda loc: distance(point, loc) < 3, data), key=lambda loc: distance(point, loc))
            # selected_locations = random.sample(sorted_locations, 10)
            # return selected_locations
            selected_locations = sorted_locations
        else:
            words = user_address.split()
            if "đường" in words:
                words.remove("đường")
                user_address = " ".join(words)
            print(user_address)
            restaurant_list = restaurant_collection.find({"Address": {"$regex": user_address, "$options": "i"}})
            count = 1
            data = []
            for restaurant in restaurant_list:
                data.append(restaurant)
                count = count +1 
            print(count)
            lat, lng = get_coordinates(user_address)
            print(f'Latitude: {lat}, Longitude: {lng}')
            point = {'Longitude': lng, 'Latitude': lat}
            sorted_locations = sorted(filter(lambda loc: distance(point, loc) < 3, data), key=lambda loc: distance(point, loc))
            # selected_locations = random.sample(sorted_locations, 10)
            # return selected_locations
            selected_locations = sorted_locations
    elif user_address is None and address:
        print(3)
        if "Quận" in address:
            print(3.1)
            restaurant_list = restaurant_collection.find({"District": address})
            count = 1
            data = []
            for restaurant in restaurant_list:
                data.append(restaurant)
                # print(restaurant)
                count = count +1 
            print(count)
            lat, lng = get_coordinates(address)
            print(f'Latitude: {lat}, Longitude: {lng}')
            point = {'Longitude': lng, 'Latitude': lat}
            sorted_locations = sorted(filter(lambda loc: distance(point, loc) < 3, data), key=lambda loc: distance(point, loc))
            # selected_locations = random.sample(sorted_locations, 10)
            # return selected_locations
            selected_locations = sorted_locations
            print(3.22222)
        else:
            print(3.2)
            words = address.split()
            if "đường" in words:
                words.remove("đường")
                address = " ".join(words)
            print(address)
            restaurant_list = restaurant_collection.find({"Address": {"$regex": address, "$options": "i"}})
            count = 1
            data = []
            for restaurant in restaurant_list:
                data.append(restaurant)
                count = count +1 
            print(count)
            lat, lng = get_coordinates(address)
            print(f'Latitude: {lat}, Longitude: {lng}')
            point = {'Longitude': lng, 'Latitude': lat}
            sorted_locations = sorted(filter(lambda loc: distance(point, loc) < 3, data), key=lambda loc: distance(point, loc))
            # selected_locations = random.sample(sorted_locations, 10)
            # return selected_locations
            selected_locations = sorted_locations
    elif user_address is None and address is None:
            print(4)
            if cuisine is None:
                top_10_restaurants = restaurant_collection.find().sort([("TotalReview", -1), ("AvgRatingOriginal", -1)]).limit(100)
                data = []
                for restaurant in top_10_restaurants:
                    data.append(restaurant)
                    # print(f"{restaurant['Name']}: TotalReview = {restaurant['TotalReview']}, AvgRatingOriginal = {restaurant['AvgRatingOriginal']}")
                # selected_locations = random.sample(data, 10)
                selected_locations = data
            else:
                top_10_restaurants = restaurant_collection.find({
                    "$or":[
                        {"Cuisines.Name": {"$regex": cuisine, "$options": "i"}},
                        {"Name": {"$regex": cuisine, "$options": "i"}}
                    ]
                }).sort([("TotalReview", -1), ("AvgRatingOriginal", -1)]).limit(10)
                data = []
                for restaurant in top_10_restaurants:
                    data.append(restaurant)
                    # print(restaurant)
                    # print(f"{restaurant['Name']}: TotalReview = {restaurant['TotalReview']}, AvgRatingOriginal = {restaurant['AvgRatingOriginal']}")
                # selected_locations = random.sample(data, 10)
                selected_locations = data
    if cuisine is None:
        print(5)
        return random.sample(selected_locations, 10)
    else:
        return_data = []
        for location in selected_locations:
            if cuisine.lower() in location["Name"].lower() or is_cuisine_in_location(cuisine, location):
                return_data.append(location)
        if len(return_data) >= 10:
            return random.sample(return_data, 10)
        else:
            return return_data

        


# class ActionGetRestaurant_HaveAddress(Action):
#     def name(self) -> Text:
#         return "action_get_restaurant_by_address"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         print("run action restaurant recommend by address")
#         district = tracker.get_slot("district")

#         dispatcher.utter_message(text="Địa chỉ của bạn là {}".format(district))
#         dispatcher.utter_message(text="Đang tìm kiếm các nhà hàng gần địa chỉ của bạn...")
#         # get district
#         print(district)
#         if district:
#             # get restaurant
#             restaurant = get_restaurant(district)
#             if restaurant:
#                 dispatcher.utter_message(text="Đây là một số nhà hàng gần địa chỉ của bạn:")
#                 for i in range(len(restaurant)):
#                     dispatcher.utter_message(text="{} - {} - {}".format(i+1, restaurant[i]["Name"], restaurant[i]["Address"]))
#             else:
#                 dispatcher.utter_message(text="Xin lỗi, em không tìm thấy nhà hàng nào gần địa chỉ của bạn")
#         else:
#             dispatcher.utter_message(text="Xin lỗi, em không tìm thấy quận nào gần địa chỉ của bạn")
#         return []
    
class Action_Option_Randomize(Action):
    def name(self) -> Text:
        return "action_get_restaurant_randomize"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("run randomize")
        address = tracker.get_slot("address")
        user_address = tracker.get_slot("user_address")
        cuisine = tracker.get_slot("cuisine")
        restaurant = get_restaurant_high_rate(user_address, address, cuisine)
        if restaurant:
            dispatcher.utter_message(text="Dưới đây là những hàng được đánh giá cao nha...")
            templates = sendTemplates(restaurant)
            message_str={
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": templates
                    }
                }
            }
            # print(message_str)
            dispatcher.utter_message(json_message=message_str)
            dispatcher.utter_message(text="Bạn cần bot hỗ trợ gì nữa không nà :3")
        else:
            dispatcher.utter_message(text="Xin lỗi, mình không tìm thấy nhà hàng nào dựa trên chỉ dẫn của bạn")
        return []



class Action_Option_By_Order(Action):
    def name(self) -> Text:
        return "action_get_restaurant_by_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("run action_get_restaurant_by_order")
        address = tracker.get_slot("address")
        user_address = tracker.get_slot("user_address")
        cuisine = tracker.get_slot("cuisine")
        restaurant = get_restaurant(user_address, address, cuisine)
        if restaurant:
            dispatcher.utter_message(text="Dưới đây là những hàng được tìm thấy dựa vào những gì bạn cung cấp...")
            templates = sendTemplates(restaurant)
            message_str={
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": templates
                    }
                }
            }
            print(message_str)
            dispatcher.utter_message(json_message=message_str)
            dispatcher.utter_message(text="Bạn cần bot hỗ trợ gì nữa không nà :3")
        else:
            dispatcher.utter_message(text="Xin lỗi, mình không tìm thấy nhà hàng nào dựa trên chỉ dẫn của bạn")
        return []

class Action_Option_Near_By(Action):
    def name(self) -> Text:
        return "action_get_restaurant_nearby"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("run action_get_restaurant_nearby")
        address = tracker.get_slot("address")
        user_address = tracker.get_slot("user_address")
        cuisine = tracker.get_slot("cuisine")
        restaurant = get_restaurant_near_by(user_address, address, cuisine)
        if restaurant:
            dispatcher.utter_message(text="Dưới đây là những hàng được tìm thấy dựa vào những gì bạn cung cấp...")
            templates = sendTemplates(restaurant)
            message_str={
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": templates
                    }
                }
            }
            print(message_str)
            dispatcher.utter_message(json_message=message_str)
            dispatcher.utter_message(text="Bạn cần bot hỗ trợ gì nữa không nà :3")
        else:
            dispatcher.utter_message(text="Xin lỗi, mình không tìm thấy nhà hàng nào dựa trên chỉ dẫn của bạn")
        return []


def sendTemplates(restaurants):
    templates = []
    for i in range(len(restaurants)):
        template = {
            "title": restaurants[i]["Name"],
            "image_url": restaurants[i]["MobilePicturePath"],
            "subtitle": restaurants[i]["Address"] + ", " + restaurants[i]["District"] + "\n" + "Avg rating: " + str(restaurants[i]["AvgRating"])+ "\n" + "Total Reviews: "+ str(restaurants[i]["TotalReview"]),
            "buttons": [
                {
                    "type": "web_url",
                    "url": "foody.vn" + restaurants[i]["DetailUrl"],
                    "title": "Xem chi tiết"
                },
                {
                    "type": "web_url",
                    "url": "foody.vn" + restaurants[i]["ReviewUrl"],
                    "title": "Link Review"
                }
            ]
        }
        templates.append(template)
    return templates

class ActionAskRoute(Action):
    def name(self) -> Text:
        return "action_set_option"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        option = tracker.latest_message['intent'].get('text')
        print("run action_set_option")
        return [SlotSet("option", option)]

class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="Anh/chị có thể cho bot biết ý định không ạ?")
        return [UserUtteranceReverted()]
