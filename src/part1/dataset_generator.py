import csv
import random
import os
from src.part1.models import *
from src.part1.bst import RecipeBST
from src.part1.linked_list import RecipeIngredientLinkedList
from src.part1.supply_graph import SupplyGraph
from src.part1.max_heap import UrgencyMaxHeap


class DatasetGenerator:
    """
    数据集生成器，严格满足项目约束：
    - 至少15食谱、20食材、6供应商、30供应关系
    - 至少3个菜系、2个难度、5个食材缺库存、3个食材多供应商
    """

    def __init__(self):
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        # 基础数据集
        self.ingredients: list[Ingredient] = []
        self.recipes: list[Recipe] = []
        self.suppliers: list[Supplier] = []
        self.supply_relations = []
        self.recipe_ingredient_relations = []  # 食谱-食材关联：(recipe_id, ing_id, quantity)

        # 固定数据集池（保证多样性）
        self.ingredient_name_pool = [
            "rice", "beef", "pork", "egg", "milk", "butter", "flour", "tomato",
            "cabbage", "garlic", "ginger", "soy_sauce", "cream", "coconut_milk",
            "noodle", "shrimp", "carrot", "onion", "pepper", "cheese"
        ]
        # 强制至少3个菜系（CHINESE/WESTERN/THAI）
        self.cuisine_list = [CuisineType.CHINESE, CuisineType.WESTERN, CuisineType.THAI]
        # 强制至少2个难度（EASY/MEDIUM）
        self.diff_list = [Difficulty.EASY, Difficulty.MEDIUM]
        self.cat_list = list(IngredientCategory)

    def generate_ingredients(self, count=20):
        """生成食材，强制5个食材低于最低库存"""
        for i in range(count):
            name = self.ingredient_name_pool[i]
            cat = random.choice(self.cat_list)
            unit = "kg" if cat in [IngredientCategory.MEAT, IngredientCategory.PRODUCE] else "L"
            min_stock = random.randint(5, 20)
            # 强制前5个食材低于最低库存（满足约束）
            if i < 5:
                current = random.randint(1, min_stock - 1)
            else:
                current = random.randint(min_stock, min_stock + 30)
            lead = random.randint(3, 14)
            ing = Ingredient(i, name, cat, unit, float(current), float(min_stock), lead)
            self.ingredients.append(ing)

    def generate_suppliers(self, count=6):
        """生成6个供应商（固定数量）"""
        locs = ["Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Chengdu", "Hangzhou"]
        for i in range(count):
            rel = round(random.uniform(0.4, 1.0), 2)
            sup = Supplier(i, f"Supplier_{i}", locs[i], rel)
            self.suppliers.append(sup)

    def generate_recipes(self, count=15):
        """生成15个食谱，强制≥3个菜系、≥2个难度"""
        recipe_names = [
            "Fried Rice", "Beef Noodle", "Tomato Egg Soup", "Braised Pork",
            "Coconut Curry", "Grilled Steak", "Sushi Roll", "Mapo Tofu",
            "Cream Pasta", "Shrimp Dumpling", "Carrot Salad", "Garlic Bread",
            "Milk Porridge", "Pepper Chicken", "Cheese Omelette"
        ]
        for i in range(count):
            name = recipe_names[i]
            # 强制覆盖至少3个菜系
            cui = self.cuisine_list[i % len(self.cuisine_list)] if i < len(self.cuisine_list) else random.choice(
                self.cuisine_list)
            # 强制覆盖至少2个难度
            diff = self.diff_list[i % len(self.diff_list)] if i < len(self.diff_list) else random.choice(self.diff_list)
            prep = random.randint(10, 90)
            serve = random.randint(2, 8)
            rec = Recipe(i, name, cui, diff, prep, serve)

            # 绑定食材单向链表并记录关联关系
            ll = RecipeIngredientLinkedList()
            ing_num = random.randint(3, 7)
            selected_ings = random.sample(self.ingredients, ing_num)
            for ing in selected_ings:
                qty = round(random.uniform(0.2, 3.0), 1)
                ll.add_ingredient(ing, qty)
                self.recipe_ingredient_relations.append((rec.recipe_id, ing.ingredient_id, qty))

            rec.ingredient_list = ll
            self.recipes.append(rec)

    def generate_supply_relationships(self, total=30):
        """生成30个供应关系，强制3个食材有多个供应商"""
        ing_ids = [x.ingredient_id for x in self.ingredients]
        sup_ids = [x.supplier_id for x in self.suppliers]

        # 强制3个食材分配多个供应商（满足约束）
        multi_ing = random.sample(ing_ids, 3)
        for ing_id in multi_ing:
            multi_sup = random.sample(sup_ids, random.randint(2, 4))
            for sid in multi_sup:
                cost = round(random.uniform(2.0, 25.0), 2)
                self.supply_relations.append((sid, ing_id, cost))

        # 填充剩余关系至30条（去重）
        while len(self.supply_relations) < total:
            sid = random.choice(sup_ids)
            ing_id = random.choice(ing_ids)
            cost = round(random.uniform(2.0, 25.0), 2)
            if (sid, ing_id, cost) not in self.supply_relations:
                self.supply_relations.append((sid, ing_id, cost))

    def write_csv(self):
        """生成4+1个CSV文件（新增recipe_ingredients.csv）"""
        # 1. recipes_dataset.csv
        with open(f"{self.data_dir}/recipes_dataset.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["recipe_id", "name", "cuisine_type", "difficulty", "prep_time_minutes", "servings"])
            for r in self.recipes:
                w.writerow(
                    [r.recipe_id, r.name, r.cuisine_type.value, r.difficulty.value, r.prep_time_minutes, r.servings])

        # 2. ingredients_dataset.csv
        with open(f"{self.data_dir}/ingredients_dataset.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ingredient_id", "name", "category", "unit", "current_stock", "minimum_stock", "lead_time"])
            for i in self.ingredients:
                w.writerow(
                    [i.ingredient_id, i.name, i.category.value, i.unit, i.current_stock, i.minimum_stock, i.lead_time])

        # 3. suppliers_dataset.csv
        with open(f"{self.data_dir}/suppliers_dataset.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["supplier_id", "name", "location", "reliability_score"])
            for s in self.suppliers:
                w.writerow([s.supplier_id, s.name, s.location, s.reliability_score])

        # 4. supply_relationships_dataset.csv
        with open(f"{self.data_dir}/supply_relationships_dataset.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["supplier_id", "ingredient_id", "cost_per_unit"])
            for row in self.supply_relations:
                w.writerow(row)

        # 5. recipe_ingredients.csv（新增：食谱-食材关联）
        with open(f"{self.data_dir}/recipe_ingredients.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["recipe_id", "ingredient_id", "quantity"])
            for row in self.recipe_ingredient_relations:
                w.writerow(row)

    def generate_all_csv(self):
        """生成所有CSV，严格满足项目约束"""
        self.generate_ingredients(20)
        self.generate_suppliers(6)
        self.generate_recipes(15)
        self.generate_supply_relationships(30)
        self.write_csv()

    def load_all_data(self) -> tuple[RecipeBST, SupplyGraph, UrgencyMaxHeap, dict[int, Recipe]]:
        """加载所有CSV数据，从recipe_ingredients.csv构建食材链表（非随机）"""
        # 重建实体映射
        ing_map = {}
        sup_map = {}
        recipe_map = {}
        bst = RecipeBST()
        supply_graph = SupplyGraph()
        heap = UrgencyMaxHeap()

        # 1. 加载食材
        with open(f"{self.data_dir}/ingredients_dataset.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                iid = int(row["ingredient_id"])
                cat = IngredientCategory(row["category"])
                lead_time = int(row.get("lead_time", 7))
                ing = Ingredient(
                    iid, row["name"], cat, row["unit"],
                    float(row["current_stock"]), float(row["minimum_stock"]),
                    lead_time
                )
                ing_map[iid] = ing

        # 2. 加载供应商
        with open(f"{self.data_dir}/suppliers_dataset.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sid = int(row["supplier_id"])
                sup = Supplier(sid, row["name"], row["location"], float(row["reliability_score"]))
                sup_map[sid] = sup
                supply_graph.add_supplier(sid)

        # 3. 加载供应关系
        with open(f"{self.data_dir}/supply_relationships_dataset.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sid = int(row["supplier_id"])
                iid = int(row["ingredient_id"])
                cost = float(row["cost_per_unit"])
                supply_graph.add_supply_relation(sid, iid, cost)

        # 4. 加载食谱（先加载基础信息）
        with open(f"{self.data_dir}/recipes_dataset.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rid = int(row["recipe_id"])
                cui = CuisineType(row["cuisine_type"])
                diff = Difficulty(row["difficulty"])
                rec = Recipe(
                    rid, row["name"], cui, diff,
                    int(row["prep_time_minutes"]), int(row["servings"])
                )
                recipe_map[rid] = rec

        # 5. 加载食谱-食材关联，构建链表（从CSV读取，非随机）
        recipe_ing_map = {}  # recipe_id -> list[(ing_id, quantity)]
        with open(f"{self.data_dir}/recipe_ingredients.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rid = int(row["recipe_id"])
                iid = int(row["ingredient_id"])
                qty = float(row["quantity"])
                if rid not in recipe_ing_map:
                    recipe_ing_map[rid] = []
                recipe_ing_map[rid].append((iid, qty))

        # 为每个食谱构建食材链表
        for rid, rec in recipe_map.items():
            ll = RecipeIngredientLinkedList()
            for iid, qty in recipe_ing_map.get(rid, []):
                if iid in ing_map:
                    ll.add_ingredient(ing_map[iid], qty)
            rec.ingredient_list = ll
            bst.insert(rec)

        # 6. 统计食材依赖数，填充最大堆
        ing_depend_count = {iid: 0 for iid in ing_map}
        for rec in recipe_map.values():
            for ing, qty in rec.ingredient_list.get_all_ingredients():
                ing_depend_count[ing.ingredient_id] += 1
        for ing in ing_map.values():
            heap.push(ing, ing_depend_count[ing.ingredient_id])

        return bst, supply_graph, heap, recipe_map