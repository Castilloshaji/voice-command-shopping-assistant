from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.product import Product

SEED_PRODUCTS: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # 1. Dairy & Eggs (20 products)
    # -------------------------------------------------------------------------
    {
        "name": "Whole Milk",
        "category": "dairy",
        "brand": "Milma",
        "price": 62.0,
        "size": "1 L",
        "is_available": True,
        "season": "all",
        "substitutes": ["Low Fat Milk", "Toned Milk"]
    },
    {
        "name": "Low Fat Milk",
        "category": "dairy",
        "brand": "Milma",
        "price": 60.0,
        "size": "1 L",
        "is_available": True,
        "season": "all",
        "substitutes": ["Toned Milk", "Whole Milk"]
    },
    {
        "name": "Toned Milk",
        "category": "dairy",
        "brand": "Amul",
        "price": 56.0,
        "size": "1 L",
        "is_available": True,
        "season": "all",
        "substitutes": ["Low Fat Milk", "Whole Milk"]
    },
    {
        "name": "Buttermilk",
        "category": "dairy",
        "brand": "Milma",
        "price": 25.0,
        "size": "500 ml",
        "is_available": True,
        "season": "summer",
        "substitutes": ["Curd", "Plain Yogurt"]
    },
    {
        "name": "Curd",
        "category": "dairy",
        "brand": "Milma",
        "price": 35.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Plain Yogurt", "Greek Yogurt"]
    },
    {
        "name": "Greek Yogurt",
        "category": "dairy",
        "brand": "Epigamia",
        "price": 60.0,
        "size": "100 g",
        "is_available": False,
        "season": "all",
        "substitutes": ["Plain Yogurt", "Curd"]
    },
    {
        "name": "Plain Yogurt",
        "category": "dairy",
        "brand": "Milma",
        "price": 40.0,
        "size": "400 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Curd", "Greek Yogurt"]
    },
    {
        "name": "Flavored Yogurt",
        "category": "dairy",
        "brand": "Epigamia",
        "price": 50.0,
        "size": "100 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Plain Yogurt"]
    },
    {
        "name": "Paneer",
        "category": "dairy",
        "brand": "Amul",
        "price": 120.0,
        "size": "200 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Cheddar Cheese"]
    },
    {
        "name": "Unsalted Butter",
        "category": "dairy",
        "brand": "Land O'Lakes",
        "price": 4.99,
        "size": "16 oz",
        "is_available": True,
        "season": "all",
        "substitutes": ["Salted Butter", "Ghee"]
    },
    {
        "name": "Salted Butter",
        "category": "dairy",
        "brand": "Amul",
        "price": 58.0,
        "size": "100 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Unsalted Butter", "Ghee"]
    },
    {
        "name": "Cheddar Cheese",
        "category": "dairy",
        "brand": "Tillamook",
        "price": 4.29,
        "size": "8 oz",
        "is_available": True,
        "season": "all",
        "substitutes": ["Mozzarella Cheese"]
    },
    {
        "name": "Mozzarella Cheese",
        "category": "dairy",
        "brand": "Amul",
        "price": 140.0,
        "size": "200 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Cheddar Cheese"]
    },
    {
        "name": "Fresh Cream",
        "category": "dairy",
        "brand": "Amul",
        "price": 65.0,
        "size": "250 ml",
        "is_available": True,
        "season": "all",
        "substitutes": ["Plain Yogurt"]
    },
    {
        "name": "Ghee",
        "category": "dairy",
        "brand": "Milma",
        "price": 310.0,
        "size": "500 ml",
        "is_available": True,
        "season": "all",
        "substitutes": ["Unsalted Butter"]
    },
    {
        "name": "Eggs",
        "category": "dairy",
        "brand": "Farm Fresh",
        "price": 75.0,
        "size": "6 pcs",
        "is_available": True,
        "season": "all",
        "substitutes": ["Brown Eggs"]
    },
    {
        "name": "Brown Eggs",
        "category": "dairy",
        "brand": "Organic Farm",
        "price": 110.0,
        "size": "6 pcs",
        "is_available": True,
        "season": "all",
        "substitutes": ["Eggs"]
    },

    # -------------------------------------------------------------------------
    # 2. Fruits (20 products)
    # -------------------------------------------------------------------------
    {
        "name": "Gala Apples",
        "category": "produce",
        "brand": "Washington Fresh",
        "price": 1.99,
        "size": "1 lb",
        "is_available": True,
        "season": "fall",
        "substitutes": ["Green Apples", "Red Delicious Apples"]
    },
    {
        "name": "Green Apples",
        "category": "produce",
        "brand": "Fresh Farms",
        "price": 190.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Gala Apples", "Red Delicious Apples"]
    },
    {
        "name": "Red Delicious Apples",
        "category": "produce",
        "brand": "Fresh Farms",
        "price": 170.0,
        "size": "1 kg",
        "is_available": True,
        "season": "fall",
        "substitutes": ["Gala Apples", "Green Apples"]
    },
    {
        "name": "Fresh Bananas",
        "category": "produce",
        "brand": "Dole",
        "price": 0.59,
        "size": "1 lb",
        "is_available": True,
        "season": "all",
        "substitutes": ["Nendran Bananas"]
    },
    {
        "name": "Nendran Bananas",
        "category": "produce",
        "brand": "Kerala Organics",
        "price": 65.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Fresh Bananas"]
    },
    {
        "name": "Oranges",
        "category": "produce",
        "brand": "Nagpur Fresh",
        "price": 90.0,
        "size": "1 kg",
        "is_available": True,
        "season": "winter",
        "substitutes": ["Mandarins"]
    },
    {
        "name": "Mandarins",
        "category": "produce",
        "brand": "Fresh Farms",
        "price": 120.0,
        "size": "1 kg",
        "is_available": True,
        "season": "winter",
        "substitutes": ["Oranges"]
    },
    {
        "name": "Alphonso Mangoes",
        "category": "produce",
        "brand": "Ratnagiri Fresh",
        "price": 450.0,
        "size": "1 kg",
        "is_available": True,
        "season": "summer",
        "substitutes": ["Papaya"]
    },
    {
        "name": "Papaya",
        "category": "produce",
        "brand": "Farm Fresh",
        "price": 50.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Pineapple"]
    },
    {
        "name": "Pineapple",
        "category": "produce",
        "brand": "Vazhakulam Fresh",
        "price": 70.0,
        "size": "1 pc",
        "is_available": True,
        "season": "all",
        "substitutes": ["Watermelon"]
    },
    {
        "name": "Watermelon",
        "category": "produce",
        "brand": "Farm Fresh",
        "price": 45.0,
        "size": "1 kg",
        "is_available": True,
        "season": "summer",
        "substitutes": ["Muskmelon"]
    },
    {
        "name": "Muskmelon",
        "category": "produce",
        "brand": "Farm Fresh",
        "price": 60.0,
        "size": "1 kg",
        "is_available": True,
        "season": "summer",
        "substitutes": ["Watermelon"]
    },
    {
        "name": "Black Grapes",
        "category": "produce",
        "brand": "Fresh Farms",
        "price": 110.0,
        "size": "500 g",
        "is_available": True,
        "season": "spring",
        "substitutes": ["Organic Strawberries"]
    },
    {
        "name": "Pomegranate",
        "category": "produce",
        "brand": "Farm Fresh",
        "price": 180.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Guava"]
    },
    {
        "name": "Guava",
        "category": "produce",
        "brand": "Farm Fresh",
        "price": 70.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Pomegranate"]
    },
    {
        "name": "Kiwi",
        "category": "produce",
        "brand": "Zespri",
        "price": 120.0,
        "size": "3 pcs",
        "is_available": True,
        "season": "all",
        "substitutes": ["Avocado"]
    },
    {
        "name": "Avocado",
        "category": "produce",
        "brand": "Fresh Farms",
        "price": 160.0,
        "size": "1 pc",
        "is_available": True,
        "season": "all",
        "substitutes": ["Kiwi"]
    },
    {
        "name": "Organic Strawberries",
        "category": "produce",
        "brand": "Driscoll's",
        "price": 4.99,
        "size": "1 lb",
        "is_available": True,
        "season": "summer",
        "substitutes": ["Blueberries"]
    },
    {
        "name": "Blueberries",
        "category": "produce",
        "brand": "Driscoll's",
        "price": 220.0,
        "size": "125 g",
        "is_available": True,
        "season": "summer",
        "substitutes": ["Organic Strawberries"]
    },
    {
        "name": "Lemons",
        "category": "produce",
        "brand": "Farm Fresh",
        "price": 30.0,
        "size": "250 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Limes"]
    },
    {
        "name": "Limes",
        "category": "produce",
        "brand": "Farm Fresh",
        "price": 35.0,
        "size": "250 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Lemons"]
    },
    {
        "name": "Coconut",
        "category": "produce",
        "brand": "Kerala Organics",
        "price": 35.0,
        "size": "1 pc",
        "is_available": True,
        "season": "all",
        "substitutes": ["Grated Coconut"]
    },

    # -------------------------------------------------------------------------
    # 3. Vegetables (25 products)
    # -------------------------------------------------------------------------
    {
        "name": "Potatoes",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 35.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Sweet Potatoes"]
    },
    {
        "name": "Sweet Potatoes",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 50.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Potatoes"]
    },
    {
        "name": "Onions",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 40.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Red Onions"]
    },
    {
        "name": "Red Onions",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 45.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Onions"]
    },
    {
        "name": "Tomatoes",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 30.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Cherry Tomatoes"]
    },
    {
        "name": "Cherry Tomatoes",
        "category": "vegetables",
        "brand": "Organic Girl",
        "price": 80.0,
        "size": "250 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Tomatoes"]
    },
    {
        "name": "Carrots",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 55.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Beetroot"]
    },
    {
        "name": "Cucumber",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 35.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Carrots"]
    },
    {
        "name": "Baby Spinach",
        "category": "produce",
        "brand": "Organic Girl",
        "price": 3.49,
        "size": "5 oz",
        "is_available": True,
        "season": "spring",
        "substitutes": ["Spinach"]
    },
    {
        "name": "Spinach",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 25.0,
        "size": "1 bunch",
        "is_available": True,
        "season": "all",
        "substitutes": ["Baby Spinach"]
    },
    {
        "name": "Cabbage",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 40.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Cauliflower"]
    },
    {
        "name": "Cauliflower",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 45.0,
        "size": "1 pc",
        "is_available": True,
        "season": "winter",
        "substitutes": ["Broccoli"]
    },
    {
        "name": "Broccoli",
        "category": "vegetables",
        "brand": "Organic Girl",
        "price": 90.0,
        "size": "500 g",
        "is_available": True,
        "season": "winter",
        "substitutes": ["Cauliflower"]
    },
    {
        "name": "Green Beans",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 60.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Green Peas"]
    },
    {
        "name": "Green Peas",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 70.0,
        "size": "500 g",
        "is_available": True,
        "season": "winter",
        "substitutes": ["Frozen Peas"]
    },
    {
        "name": "Green Capsicum",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 50.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Red Capsicum"]
    },
    {
        "name": "Red Capsicum",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 90.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Green Capsicum"]
    },
    {
        "name": "Beetroot",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 45.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Carrots"]
    },
    {
        "name": "Radish",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 30.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Beetroot"]
    },
    {
        "name": "Pumpkin",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 35.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Bottle Gourd"]
    },
    {
        "name": "Bottle Gourd",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 40.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Pumpkin"]
    },
    {
        "name": "Ginger",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 120.0,
        "size": "250 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Garlic"]
    },
    {
        "name": "Garlic",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 160.0,
        "size": "250 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Ginger"]
    },
    {
        "name": "Green Chilli",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 25.0,
        "size": "100 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Green Capsicum"]
    },
    {
        "name": "Coriander",
        "category": "vegetables",
        "brand": "Farm Fresh",
        "price": 20.0,
        "size": "1 bunch",
        "is_available": True,
        "season": "all",
        "substitutes": ["Mint"]
    },

    # -------------------------------------------------------------------------
    # 4. Rice, Grains & Flour (15 products)
    # -------------------------------------------------------------------------
    {
        "name": "White Rice",
        "category": "grains",
        "brand": "India Gate",
        "price": 70.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Basmati Rice", "Matta Rice"]
    },
    {
        "name": "Basmati Rice",
        "category": "grains",
        "brand": "India Gate",
        "price": 140.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["White Rice", "Sona Masoori Rice"]
    },
    {
        "name": "Matta Rice",
        "category": "grains",
        "brand": "Nirapara",
        "price": 65.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Brown Rice", "White Rice"]
    },
    {
        "name": "Brown Rice",
        "category": "grains",
        "brand": "Daawat",
        "price": 110.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Matta Rice"]
    },
    {
        "name": "Sona Masoori Rice",
        "category": "grains",
        "brand": "Royal",
        "price": 75.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["White Rice"]
    },
    {
        "name": "Atta Wheat Flour",
        "category": "grains",
        "brand": "Aashirvaad",
        "price": 65.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Maida"]
    },
    {
        "name": "Maida",
        "category": "grains",
        "brand": "Aashirvaad",
        "price": 50.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Atta Wheat Flour"]
    },
    {
        "name": "Rava Semolina",
        "category": "grains",
        "brand": "Nirapara",
        "price": 45.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Rice Flour"]
    },
    {
        "name": "Rolled Oats",
        "category": "grains",
        "brand": "Quaker",
        "price": 180.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Muesli"]
    },
    {
        "name": "Quinoa",
        "category": "grains",
        "brand": "Organic India",
        "price": 260.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Rolled Oats"]
    },
    {
        "name": "Corn Flour",
        "category": "grains",
        "brand": "Weikfield",
        "price": 40.0,
        "size": "200 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Maida"]
    },
    {
        "name": "Rice Flour",
        "category": "grains",
        "brand": "Nirapara",
        "price": 55.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Rava Semolina"]
    },
    {
        "name": "Besan",
        "category": "grains",
        "brand": "Fortune",
        "price": 60.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Atta Wheat Flour"]
    },
    {
        "name": "Semolina",
        "category": "grains",
        "brand": "MTR",
        "price": 45.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Rava Semolina"]
    },
    {
        "name": "Oats",
        "category": "grains",
        "brand": "Saffola",
        "price": 160.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Rolled Oats"]
    },

    # -------------------------------------------------------------------------
    # 5. Pulses & Legumes (10 products)
    # -------------------------------------------------------------------------
    {
        "name": "Toor Dal",
        "category": "pulses",
        "brand": "Tata Sampann",
        "price": 160.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Moong Dal"]
    },
    {
        "name": "Moong Dal",
        "category": "pulses",
        "brand": "Tata Sampann",
        "price": 140.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Toor Dal"]
    },
    {
        "name": "Masoor Dal",
        "category": "pulses",
        "brand": "Tata Sampann",
        "price": 110.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Toor Dal"]
    },
    {
        "name": "Chana Dal",
        "category": "pulses",
        "brand": "Tata Sampann",
        "price": 95.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Urad Dal"]
    },
    {
        "name": "Urad Dal",
        "category": "pulses",
        "brand": "Tata Sampann",
        "price": 150.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Chana Dal"]
    },
    {
        "name": "Green Gram",
        "category": "pulses",
        "brand": "Tata Sampann",
        "price": 130.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Moong Dal"]
    },
    {
        "name": "Black Gram",
        "category": "pulses",
        "brand": "Tata Sampann",
        "price": 155.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Urad Dal"]
    },
    {
        "name": "Chickpeas",
        "category": "pulses",
        "brand": "Tata Sampann",
        "price": 130.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Rajma"]
    },
    {
        "name": "Kabuli Chana",
        "category": "pulses",
        "brand": "Tata Sampann",
        "price": 145.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Chickpeas"]
    },
    {
        "name": "Rajma",
        "category": "pulses",
        "brand": "Tata Sampann",
        "price": 150.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Chickpeas"]
    },

    # -------------------------------------------------------------------------
    # 6. Bread & Bakery (12 products)
    # -------------------------------------------------------------------------
    {
        "name": "Whole Wheat Bread",
        "category": "bakery",
        "brand": "Nature's Own",
        "price": 2.89,
        "size": "20 oz",
        "is_available": True,
        "season": "all",
        "substitutes": ["White Bread", "Brown Bread"]
    },
    {
        "name": "White Bread",
        "category": "bakery",
        "brand": "Modern Bakery",
        "price": 45.0,
        "size": "400 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Whole Wheat Bread"]
    },
    {
        "name": "Brown Bread",
        "category": "bakery",
        "brand": "Britannia",
        "price": 50.0,
        "size": "400 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Whole Wheat Bread"]
    },
    {
        "name": "Multigrain Bread",
        "category": "bakery",
        "brand": "Britannia",
        "price": 60.0,
        "size": "400 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Whole Wheat Bread"]
    },
    {
        "name": "Sourdough Loaf",
        "category": "bakery",
        "brand": "Artisan Bakery",
        "price": 3.99,
        "size": "1 loaf",
        "is_available": True,
        "season": "all",
        "substitutes": ["Whole Wheat Bread"]
    },
    {
        "name": "Burger Buns",
        "category": "bakery",
        "brand": "Britannia",
        "price": 40.0,
        "size": "4 pcs",
        "is_available": True,
        "season": "all",
        "substitutes": ["Hot Dog Buns"]
    },
    {
        "name": "Hot Dog Buns",
        "category": "bakery",
        "brand": "Britannia",
        "price": 40.0,
        "size": "4 pcs",
        "is_available": True,
        "season": "all",
        "substitutes": ["Burger Buns"]
    },
    {
        "name": "Butter Croissant",
        "category": "bakery",
        "brand": "Fresh Bakery",
        "price": 1.99,
        "size": "1 pc",
        "is_available": False,
        "season": "all",
        "substitutes": ["Croissants"]
    },
    {
        "name": "Croissants",
        "category": "bakery",
        "brand": "Fresh Bakery",
        "price": 80.0,
        "size": "2 pcs",
        "is_available": True,
        "season": "all",
        "substitutes": ["Butter Croissant"]
    },
    {
        "name": "Chocolate Muffins",
        "category": "bakery",
        "brand": "Britannia",
        "price": 60.0,
        "size": "2 pcs",
        "is_available": True,
        "season": "all",
        "substitutes": ["Muffins"]
    },
    {
        "name": "Muffins",
        "category": "bakery",
        "brand": "Britannia",
        "price": 50.0,
        "size": "2 pcs",
        "is_available": True,
        "season": "all",
        "substitutes": ["Chocolate Muffins"]
    },
    {
        "name": "Chocolate Cookies",
        "category": "bakery",
        "brand": "Hide & Seek",
        "price": 40.0,
        "size": "120 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Cream Biscuits"]
    },

    # -------------------------------------------------------------------------
    # 7. Snacks (12 products)
    # -------------------------------------------------------------------------
    {
        "name": "Classic Potato Chips",
        "category": "snacks",
        "brand": "Lay's",
        "price": 3.49,
        "size": "8 oz",
        "is_available": True,
        "season": "all",
        "substitutes": ["Salted Chips", "Masala Chips"]
    },
    {
        "name": "Salted Chips",
        "category": "snacks",
        "brand": "Lay's",
        "price": 30.0,
        "size": "50 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Classic Potato Chips"]
    },
    {
        "name": "Masala Chips",
        "category": "snacks",
        "brand": "Lay's",
        "price": 30.0,
        "size": "50 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Classic Potato Chips"]
    },
    {
        "name": "Nachos",
        "category": "snacks",
        "brand": "Doritos",
        "price": 50.0,
        "size": "80 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Classic Potato Chips"]
    },
    {
        "name": "Popcorn",
        "category": "snacks",
        "brand": "Act II",
        "price": 35.0,
        "size": "150 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Nachos"]
    },
    {
        "name": "Peanuts",
        "category": "snacks",
        "brand": "Haldiram's",
        "price": 30.0,
        "size": "150 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Masala Peanuts"]
    },
    {
        "name": "Masala Peanuts",
        "category": "snacks",
        "brand": "Haldiram's",
        "price": 40.0,
        "size": "150 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Peanuts"]
    },
    {
        "name": "Mixed Nuts",
        "category": "snacks",
        "brand": "Planters",
        "price": 6.99,
        "size": "10 oz",
        "is_available": True,
        "season": "winter",
        "substitutes": ["Cashews", "Almonds"]
    },
    {
        "name": "Namkeen",
        "category": "snacks",
        "brand": "Haldiram's",
        "price": 45.0,
        "size": "200 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Mixture"]
    },
    {
        "name": "Mixture",
        "category": "snacks",
        "brand": "Haldiram's",
        "price": 50.0,
        "size": "200 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Namkeen"]
    },
    {
        "name": "Crackers",
        "category": "snacks",
        "brand": "Monaco",
        "price": 25.0,
        "size": "120 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Cream Biscuits"]
    },
    {
        "name": "Cream Biscuits",
        "category": "snacks",
        "brand": "Oreo",
        "price": 35.0,
        "size": "120 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Chocolate Cookies"]
    },

    # -------------------------------------------------------------------------
    # 8. Breakfast & Cereals (10 products)
    # -------------------------------------------------------------------------
    {
        "name": "Cornflakes",
        "category": "breakfast",
        "brand": "Kellogg's",
        "price": 175.0,
        "size": "475 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Muesli"]
    },
    {
        "name": "Muesli",
        "category": "breakfast",
        "brand": "Kellogg's",
        "price": 290.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Cornflakes"]
    },
    {
        "name": "Granola",
        "category": "breakfast",
        "brand": "Bagrrys",
        "price": 310.0,
        "size": "400 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Muesli"]
    },
    {
        "name": "Chocolate Cereal",
        "category": "breakfast",
        "brand": "Chocos",
        "price": 180.0,
        "size": "375 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Cornflakes"]
    },
    {
        "name": "Peanut Butter",
        "category": "breakfast",
        "brand": "Pintola",
        "price": 220.0,
        "size": "350 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Crunchy Peanut Butter"]
    },
    {
        "name": "Crunchy Peanut Butter",
        "category": "breakfast",
        "brand": "Pintola",
        "price": 240.0,
        "size": "350 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Peanut Butter"]
    },
    {
        "name": "Strawberry Jam",
        "category": "breakfast",
        "brand": "Kissan",
        "price": 95.0,
        "size": "200 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Mixed Fruit Jam"]
    },
    {
        "name": "Mixed Fruit Jam",
        "category": "breakfast",
        "brand": "Kissan",
        "price": 90.0,
        "size": "200 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Strawberry Jam"]
    },
    {
        "name": "Honey",
        "category": "breakfast",
        "brand": "Dabur",
        "price": 199.0,
        "size": "250 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Maple Syrup"]
    },
    {
        "name": "Maple Syrup",
        "category": "breakfast",
        "brand": "Hershey's",
        "price": 399.0,
        "size": "250 ml",
        "is_available": True,
        "season": "all",
        "substitutes": ["Honey"]
    },

    # -------------------------------------------------------------------------
    # 9. Meat & Seafood (10 products)
    # -------------------------------------------------------------------------
    {
        "name": "Chicken",
        "category": "meat",
        "brand": "Licious",
        "price": 220.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Whole Chicken"]
    },
    {
        "name": "Chicken Breast",
        "category": "meat",
        "brand": "Licious",
        "price": 260.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Chicken Thigh"]
    },
    {
        "name": "Chicken Thigh",
        "category": "meat",
        "brand": "Licious",
        "price": 240.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Chicken Breast"]
    },
    {
        "name": "Whole Chicken",
        "category": "meat",
        "brand": "Licious",
        "price": 250.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Chicken"]
    },
    {
        "name": "Mutton",
        "category": "meat",
        "brand": "Fresh Butchery",
        "price": 750.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Beef"]
    },
    {
        "name": "Beef",
        "category": "meat",
        "brand": "Fresh Butchery",
        "price": 420.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Mutton"]
    },
    {
        "name": "Fish",
        "category": "seafood",
        "brand": "Ocean Catch",
        "price": 350.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Salmon"]
    },
    {
        "name": "Salmon",
        "category": "seafood",
        "brand": "Ocean Catch",
        "price": 850.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Tuna"]
    },
    {
        "name": "Tuna",
        "category": "seafood",
        "brand": "Ocean Catch",
        "price": 450.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Salmon"]
    },
    {
        "name": "Prawns",
        "category": "seafood",
        "brand": "Ocean Catch",
        "price": 420.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Shrimp"]
    },

    # -------------------------------------------------------------------------
    # 10. Frozen Foods (10 products)
    # -------------------------------------------------------------------------
    {
        "name": "Frozen Peas",
        "category": "frozen",
        "brand": "Safal",
        "price": 110.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Frozen Corn"]
    },
    {
        "name": "Frozen Corn",
        "category": "frozen",
        "brand": "Safal",
        "price": 120.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Frozen Peas"]
    },
    {
        "name": "Frozen Mixed Vegetables",
        "category": "frozen",
        "brand": "Safal",
        "price": 130.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Frozen Peas"]
    },
    {
        "name": "Frozen French Fries",
        "category": "frozen",
        "brand": "McCain",
        "price": 140.0,
        "size": "750 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Frozen Pizza"]
    },
    {
        "name": "Frozen Pizza",
        "category": "frozen",
        "brand": "McCain",
        "price": 220.0,
        "size": "300 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Frozen French Fries"]
    },
    {
        "name": "Chicken Nuggets",
        "category": "frozen",
        "brand": "McCain",
        "price": 190.0,
        "size": "400 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Frozen French Fries"]
    },
    {
        "name": "Ice Cream",
        "category": "frozen",
        "brand": "Amul",
        "price": 140.0,
        "size": "1 L",
        "is_available": True,
        "season": "summer",
        "substitutes": ["Vanilla Ice Cream"]
    },
    {
        "name": "Vanilla Ice Cream",
        "category": "frozen",
        "brand": "Amul",
        "price": 150.0,
        "size": "1 L",
        "is_available": True,
        "season": "summer",
        "substitutes": ["Chocolate Ice Cream"]
    },
    {
        "name": "Chocolate Ice Cream",
        "category": "frozen",
        "brand": "Amul",
        "price": 160.0,
        "size": "1 L",
        "is_available": True,
        "season": "summer",
        "substitutes": ["Vanilla Ice Cream"]
    },
    {
        "name": "Mango Ice Cream",
        "category": "frozen",
        "brand": "Amul",
        "price": 165.0,
        "size": "1 L",
        "is_available": True,
        "season": "summer",
        "substitutes": ["Vanilla Ice Cream"]
    },

    # -------------------------------------------------------------------------
    # 11. Beverages (15 products)
    # -------------------------------------------------------------------------
    {
        "name": "Drinking Water",
        "category": "beverages",
        "brand": "Bisleri",
        "price": 20.0,
        "size": "1 L",
        "is_available": True,
        "season": "all",
        "substitutes": ["Mineral Water"]
    },
    {
        "name": "Mineral Water",
        "category": "beverages",
        "brand": "Kinley",
        "price": 20.0,
        "size": "1 L",
        "is_available": True,
        "season": "all",
        "substitutes": ["Drinking Water"]
    },
    {
        "name": "Sparkling Water",
        "category": "beverages",
        "brand": "LaCroix",
        "price": 4.99,
        "size": "12 pack",
        "is_available": False,
        "season": "summer",
        "substitutes": ["Club Soda", "Drinking Water"]
    },
    {
        "name": "Club Soda",
        "category": "beverages",
        "brand": "Kinley",
        "price": 20.0,
        "size": "750 ml",
        "is_available": True,
        "season": "all",
        "substitutes": ["Sparkling Water"]
    },
    {
        "name": "Soda",
        "category": "beverages",
        "brand": "Schweppes",
        "price": 30.0,
        "size": "600 ml",
        "is_available": True,
        "season": "all",
        "substitutes": ["Club Soda"]
    },
    {
        "name": "Cola",
        "category": "beverages",
        "brand": "Coca-Cola",
        "price": 40.0,
        "size": "750 ml",
        "is_available": True,
        "season": "all",
        "substitutes": ["Soda"]
    },
    {
        "name": "Orange Juice",
        "category": "beverages",
        "brand": "Tropicana",
        "price": 3.79,
        "size": "52 oz",
        "is_available": True,
        "season": "all",
        "substitutes": ["Apple Juice"]
    },
    {
        "name": "Apple Juice",
        "category": "beverages",
        "brand": "Tropicana",
        "price": 110.0,
        "size": "1 L",
        "is_available": True,
        "season": "all",
        "substitutes": ["Orange Juice"]
    },
    {
        "name": "Mango Juice",
        "category": "beverages",
        "brand": "Frooti",
        "price": 75.0,
        "size": "1 L",
        "is_available": True,
        "season": "summer",
        "substitutes": ["Orange Juice"]
    },
    {
        "name": "Mixed Fruit Juice",
        "category": "beverages",
        "brand": "Real",
        "price": 115.0,
        "size": "1 L",
        "is_available": True,
        "season": "all",
        "substitutes": ["Orange Juice"]
    },
    {
        "name": "Coconut Water",
        "category": "beverages",
        "brand": "Paper Boat",
        "price": 50.0,
        "size": "200 ml",
        "is_available": True,
        "season": "summer",
        "substitutes": ["Drinking Water"]
    },
    {
        "name": "Dark Roast Coffee",
        "category": "beverages",
        "brand": "Starbucks",
        "price": 8.99,
        "size": "12 oz bag",
        "is_available": True,
        "season": "all",
        "substitutes": ["Instant Coffee"]
    },
    {
        "name": "Instant Coffee",
        "category": "beverages",
        "brand": "Nescafé",
        "price": 185.0,
        "size": "100 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Dark Roast Coffee"]
    },
    {
        "name": "Green Tea",
        "category": "beverages",
        "brand": "Lipton",
        "price": 160.0,
        "size": "25 bags",
        "is_available": True,
        "season": "all",
        "substitutes": ["Black Tea"]
    },
    {
        "name": "Black Tea",
        "category": "beverages",
        "brand": "Tetley",
        "price": 130.0,
        "size": "25 bags",
        "is_available": True,
        "season": "all",
        "substitutes": ["Green Tea"]
    },

    # -------------------------------------------------------------------------
    # 12. Condiments & Sauces (8 products)
    # -------------------------------------------------------------------------
    {
        "name": "Tomato Ketchup",
        "category": "condiments",
        "brand": "Heinz",
        "price": 120.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Tomato Sauce"]
    },
    {
        "name": "Tomato Sauce",
        "category": "condiments",
        "brand": "Kissan",
        "price": 90.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Tomato Ketchup"]
    },
    {
        "name": "Mayonnaise",
        "category": "condiments",
        "brand": "Veeba",
        "price": 99.0,
        "size": "250 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Mustard"]
    },
    {
        "name": "Mustard",
        "category": "condiments",
        "brand": "American Garden",
        "price": 140.0,
        "size": "220 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Mayonnaise"]
    },
    {
        "name": "Chilli Sauce",
        "category": "condiments",
        "brand": "Ching's Secret",
        "price": 60.0,
        "size": "200 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Soya Sauce"]
    },
    {
        "name": "Soya Sauce",
        "category": "condiments",
        "brand": "Ching's Secret",
        "price": 65.0,
        "size": "200 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Chilli Sauce"]
    },
    {
        "name": "Pasta Sauce",
        "category": "condiments",
        "brand": "Barilla",
        "price": 190.0,
        "size": "400 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Tomato Puree"]
    },
    {
        "name": "Vinegar",
        "category": "condiments",
        "brand": "Dabur",
        "price": 50.0,
        "size": "500 ml",
        "is_available": True,
        "season": "all",
        "substitutes": ["Lemon Juice"]
    },

    # -------------------------------------------------------------------------
    # 13. Spices & Masalas (12 products)
    # -------------------------------------------------------------------------
    {
        "name": "Turmeric Powder",
        "category": "spices",
        "brand": "Eastern",
        "price": 45.0,
        "size": "200 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Chilli Powder"]
    },
    {
        "name": "Chilli Powder",
        "category": "spices",
        "brand": "Eastern",
        "price": 60.0,
        "size": "200 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Turmeric Powder"]
    },
    {
        "name": "Black Pepper",
        "category": "spices",
        "brand": "Eastern",
        "price": 110.0,
        "size": "100 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Pepper Powder"]
    },
    {
        "name": "Cumin",
        "category": "spices",
        "brand": "Everest",
        "price": 85.0,
        "size": "100 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Coriander Powder"]
    },
    {
        "name": "Coriander Powder",
        "category": "spices",
        "brand": "Eastern",
        "price": 50.0,
        "size": "200 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Cumin"]
    },
    {
        "name": "Garam Masala",
        "category": "spices",
        "brand": "Everest",
        "price": 75.0,
        "size": "100 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Chicken Masala"]
    },
    {
        "name": "Chicken Masala",
        "category": "spices",
        "brand": "Eastern",
        "price": 65.0,
        "size": "100 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Biryani Masala"]
    },
    {
        "name": "Biryani Masala",
        "category": "spices",
        "brand": "Everest",
        "price": 80.0,
        "size": "100 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Chicken Masala"]
    },
    {
        "name": "Pepper Powder",
        "category": "spices",
        "brand": "Eastern",
        "price": 95.0,
        "size": "100 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Black Pepper"]
    },
    {
        "name": "Cardamom",
        "category": "spices",
        "brand": "Kerala Organics",
        "price": 220.0,
        "size": "50 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Cloves"]
    },
    {
        "name": "Cloves",
        "category": "spices",
        "brand": "Kerala Organics",
        "price": 140.0,
        "size": "50 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Cinnamon"]
    },
    {
        "name": "Cinnamon",
        "category": "spices",
        "brand": "Kerala Organics",
        "price": 90.0,
        "size": "100 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Cardamom"]
    },

    # -------------------------------------------------------------------------
    # 14. Cooking Essentials (8 products)
    # -------------------------------------------------------------------------
    {
        "name": "Cooking Oil",
        "category": "essentials",
        "brand": "Fortune",
        "price": 140.0,
        "size": "1 L",
        "is_available": True,
        "season": "all",
        "substitutes": ["Sunflower Oil", "Coconut Oil"]
    },
    {
        "name": "Sunflower Oil",
        "category": "essentials",
        "brand": "Fortune",
        "price": 145.0,
        "size": "1 L",
        "is_available": True,
        "season": "all",
        "substitutes": ["Cooking Oil"]
    },
    {
        "name": "Coconut Oil",
        "category": "essentials",
        "brand": "KPL Shudhi",
        "price": 210.0,
        "size": "1 L",
        "is_available": True,
        "season": "all",
        "substitutes": ["Sunflower Oil"]
    },
    {
        "name": "Olive Oil",
        "category": "essentials",
        "brand": "Borges",
        "price": 650.0,
        "size": "1 L",
        "is_available": True,
        "season": "all",
        "substitutes": ["Sunflower Oil"]
    },
    {
        "name": "Salt",
        "category": "essentials",
        "brand": "Tata Salt",
        "price": 28.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Sugar"]
    },
    {
        "name": "Sugar",
        "category": "essentials",
        "brand": "Madhur",
        "price": 48.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Brown Sugar", "Jaggery"]
    },
    {
        "name": "Brown Sugar",
        "category": "essentials",
        "brand": "Organic India",
        "price": 95.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Sugar"]
    },
    {
        "name": "Jaggery",
        "category": "essentials",
        "brand": "Organic India",
        "price": 70.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Sugar"]
    },

    # -------------------------------------------------------------------------
    # 15. Pasta & Instant Foods (8 products)
    # -------------------------------------------------------------------------
    {
        "name": "Pasta",
        "category": "pasta",
        "brand": "Barilla",
        "price": 140.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Spaghetti", "Penne Pasta"]
    },
    {
        "name": "Spaghetti",
        "category": "pasta",
        "brand": "Barilla",
        "price": 150.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Penne Pasta"]
    },
    {
        "name": "Macaroni",
        "category": "pasta",
        "brand": "Bambino",
        "price": 60.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Penne Pasta"]
    },
    {
        "name": "Penne Pasta",
        "category": "pasta",
        "brand": "Barilla",
        "price": 150.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Spaghetti"]
    },
    {
        "name": "Instant Noodles",
        "category": "pasta",
        "brand": "Maggi",
        "price": 55.0,
        "size": "4 pack",
        "is_available": True,
        "season": "all",
        "substitutes": ["Ramen"]
    },
    {
        "name": "Ramen",
        "category": "pasta",
        "brand": "Nissin",
        "price": 70.0,
        "size": "100 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Instant Noodles"]
    },
    {
        "name": "Soup",
        "category": "pasta",
        "brand": "Knorr",
        "price": 45.0,
        "size": "4 pcs",
        "is_available": True,
        "season": "winter",
        "substitutes": ["Tomato Soup"]
    },
    {
        "name": "Tomato Soup",
        "category": "pasta",
        "brand": "Knorr",
        "price": 45.0,
        "size": "4 pcs",
        "is_available": True,
        "season": "winter",
        "substitutes": ["Soup"]
    },

    # -------------------------------------------------------------------------
    # 16. Canned & Packaged Foods (5 products)
    # -------------------------------------------------------------------------
    {
        "name": "Canned Beans",
        "category": "canned",
        "brand": "Heinz",
        "price": 120.0,
        "size": "400 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Canned Corn"]
    },
    {
        "name": "Canned Corn",
        "category": "canned",
        "brand": "Del Monte",
        "price": 95.0,
        "size": "400 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Canned Beans"]
    },
    {
        "name": "Canned Tuna",
        "category": "canned",
        "brand": "Ocean's Secret",
        "price": 160.0,
        "size": "185 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Canned Beans"]
    },
    {
        "name": "Tomato Puree",
        "category": "canned",
        "brand": "Dabur Homemade",
        "price": 40.0,
        "size": "200 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Tomato Paste"]
    },
    {
        "name": "Tomato Paste",
        "category": "canned",
        "brand": "Dabur Homemade",
        "price": 50.0,
        "size": "200 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Tomato Puree"]
    },

    # -------------------------------------------------------------------------
    # 17. Dry Fruits & Nuts (8 products)
    # -------------------------------------------------------------------------
    {
        "name": "Almonds",
        "category": "nuts",
        "brand": "Nutraj",
        "price": 380.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Cashews", "Walnuts"]
    },
    {
        "name": "Cashews",
        "category": "nuts",
        "brand": "Nutraj",
        "price": 420.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Almonds"]
    },
    {
        "name": "Walnuts",
        "category": "nuts",
        "brand": "Nutraj",
        "price": 490.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Almonds"]
    },
    {
        "name": "Pistachios",
        "category": "nuts",
        "brand": "Nutraj",
        "price": 550.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Cashews"]
    },
    {
        "name": "Raisins",
        "category": "nuts",
        "brand": "Nutraj",
        "price": 180.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Dates"]
    },
    {
        "name": "Dates",
        "category": "nuts",
        "brand": "Lion",
        "price": 210.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Raisins"]
    },
    {
        "name": "Dried Figs",
        "category": "nuts",
        "brand": "Nutraj",
        "price": 600.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Dates"]
    },
    {
        "name": "Sunflower Seeds",
        "category": "nuts",
        "brand": "True Elements",
        "price": 160.0,
        "size": "250 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Almonds"]
    },

    # -------------------------------------------------------------------------
    # 18. Indian / Kerala Grocery (10 products)
    # -------------------------------------------------------------------------
    {
        "name": "Dosa Batter",
        "category": "kerala_grocery",
        "brand": "iD Fresh",
        "price": 85.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Idli Batter"]
    },
    {
        "name": "Idli Batter",
        "category": "kerala_grocery",
        "brand": "iD Fresh",
        "price": 85.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Dosa Batter"]
    },
    {
        "name": "Appam Batter",
        "category": "kerala_grocery",
        "brand": "iD Fresh",
        "price": 90.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Dosa Batter"]
    },
    {
        "name": "Puttu Flour",
        "category": "kerala_grocery",
        "brand": "Nirapara",
        "price": 60.0,
        "size": "500 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Dosa Batter"]
    },
    {
        "name": "Grated Coconut",
        "category": "kerala_grocery",
        "brand": "iD Fresh",
        "price": 65.0,
        "size": "200 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Coconut"]
    },
    {
        "name": "Tamarind",
        "category": "kerala_grocery",
        "brand": "Double Horse",
        "price": 50.0,
        "size": "200 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Lime Juice"]
    },
    {
        "name": "Mango Pickle",
        "category": "kerala_grocery",
        "brand": "Double Horse",
        "price": 75.0,
        "size": "400 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Lime Pickle"]
    },
    {
        "name": "Lime Pickle",
        "category": "kerala_grocery",
        "brand": "Double Horse",
        "price": 70.0,
        "size": "400 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Mango Pickle"]
    },
    {
        "name": "Papad",
        "category": "kerala_grocery",
        "brand": "Lijjat",
        "price": 45.0,
        "size": "200 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Banana Chips"]
    },
    {
        "name": "Banana Chips",
        "category": "kerala_grocery",
        "brand": "Kerala Organics",
        "price": 90.0,
        "size": "250 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Papad"]
    },

    # -------------------------------------------------------------------------
    # 19. Personal Care (10 products)
    # -------------------------------------------------------------------------
    {
        "name": "Beauty Bar Soap",
        "category": "personal care",
        "brand": "Dove",
        "price": 4.29,
        "size": "4 pack",
        "is_available": True,
        "season": "all",
        "substitutes": ["Bath Soap", "Body Wash"]
    },
    {
        "name": "Bath Soap",
        "category": "personal care",
        "brand": "Lux",
        "price": 45.0,
        "size": "100 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Beauty Bar Soap"]
    },
    {
        "name": "Mint Toothpaste",
        "category": "personal care",
        "brand": "Crest",
        "price": 3.19,
        "size": "4.2 oz",
        "is_available": True,
        "season": "all",
        "substitutes": ["Whitening Toothpaste"]
    },
    {
        "name": "Whitening Toothpaste",
        "category": "personal care",
        "brand": "Colgate",
        "price": 95.0,
        "size": "150 g",
        "is_available": True,
        "season": "all",
        "substitutes": ["Mint Toothpaste"]
    },
    {
        "name": "Toothbrush",
        "category": "personal care",
        "brand": "Oral-B",
        "price": 50.0,
        "size": "1 pc",
        "is_available": True,
        "season": "all",
        "substitutes": ["Mint Toothpaste"]
    },
    {
        "name": "Shampoo",
        "category": "personal care",
        "brand": "Head & Shoulders",
        "price": 180.0,
        "size": "340 ml",
        "is_available": True,
        "season": "all",
        "substitutes": ["Conditioner"]
    },
    {
        "name": "Conditioner",
        "category": "personal care",
        "brand": "Pantene",
        "price": 190.0,
        "size": "200 ml",
        "is_available": True,
        "season": "all",
        "substitutes": ["Shampoo"]
    },
    {
        "name": "Hair Oil",
        "category": "personal care",
        "brand": "Parachute",
        "price": 125.0,
        "size": "250 ml",
        "is_available": True,
        "season": "all",
        "substitutes": ["Shampoo"]
    },
    {
        "name": "Body Wash",
        "category": "personal care",
        "brand": "Nivea",
        "price": 220.0,
        "size": "250 ml",
        "is_available": True,
        "season": "all",
        "substitutes": ["Beauty Bar Soap"]
    },
    {
        "name": "Moisturizer",
        "category": "personal care",
        "brand": "Pond's",
        "price": 199.0,
        "size": "100 g",
        "is_available": True,
        "season": "winter",
        "substitutes": ["Body Wash"]
    },

    # -------------------------------------------------------------------------
    # 20. Household Cleaning, Paper & Supplies (12 products)
    # -------------------------------------------------------------------------
    {
        "name": "Paper Towels",
        "category": "household",
        "brand": "Bounty",
        "price": 8.99,
        "size": "6 rolls",
        "is_available": True,
        "season": "all",
        "substitutes": ["Toilet Paper"]
    },
    {
        "name": "Toilet Paper",
        "category": "household",
        "brand": "Charmin",
        "price": 9.99,
        "size": "12 rolls",
        "is_available": True,
        "season": "all",
        "substitutes": ["Paper Towels"]
    },
    {
        "name": "Dish Soap",
        "category": "household",
        "brand": "Dawn",
        "price": 2.99,
        "size": "16 oz",
        "is_available": True,
        "season": "all",
        "substitutes": ["Dishwashing Liquid"]
    },
    {
        "name": "Dishwashing Liquid",
        "category": "household",
        "brand": "Vim",
        "price": 110.0,
        "size": "500 ml",
        "is_available": True,
        "season": "all",
        "substitutes": ["Dish Soap"]
    },
    {
        "name": "Liquid Laundry Detergent",
        "category": "household",
        "brand": "Tide",
        "price": 12.99,
        "size": "92 oz",
        "is_available": True,
        "season": "all",
        "substitutes": ["Washing Powder"]
    },
    {
        "name": "Washing Powder",
        "category": "household",
        "brand": "Surf Excel",
        "price": 160.0,
        "size": "1 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Liquid Laundry Detergent"]
    },
    {
        "name": "Floor Cleaner",
        "category": "household",
        "brand": "Lysol",
        "price": 180.0,
        "size": "1 L",
        "is_available": True,
        "season": "all",
        "substitutes": ["Disinfectant"]
    },
    {
        "name": "Toilet Cleaner",
        "category": "household",
        "brand": "Harpic",
        "price": 95.0,
        "size": "500 ml",
        "is_available": True,
        "season": "all",
        "substitutes": ["Floor Cleaner"]
    },
    {
        "name": "Glass Cleaner",
        "category": "household",
        "brand": "Collin",
        "price": 105.0,
        "size": "500 ml",
        "is_available": True,
        "season": "all",
        "substitutes": ["Disinfectant"]
    },
    {
        "name": "Disinfectant",
        "category": "household",
        "brand": "Dettol",
        "price": 170.0,
        "size": "500 ml",
        "is_available": True,
        "season": "all",
        "substitutes": ["Floor Cleaner"]
    },
    {
        "name": "Baby Diapers",
        "category": "baby",
        "brand": "Pampers",
        "price": 450.0,
        "size": "32 pcs",
        "is_available": True,
        "season": "all",
        "substitutes": ["Baby Wipes"]
    },
    {
        "name": "Dog Food",
        "category": "pet",
        "brand": "Pedigree",
        "price": 380.0,
        "size": "1.2 kg",
        "is_available": True,
        "season": "all",
        "substitutes": ["Cat Food"]
    }
]

def seed_products(db: Session) -> None:
    """Seed default product catalog if table is empty."""
    existing_count = db.query(Product).count()
    if existing_count == 0:
        products = [Product(**data) for data in SEED_PRODUCTS]
        db.add_all(products)
        db.commit()
