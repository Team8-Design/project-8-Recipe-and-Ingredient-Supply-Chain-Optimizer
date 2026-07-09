import csv
import random
import os
import logging
from typing import List, Dict, Tuple, Optional
# 直接引用models中的类（无需src路径，保证可独立运行）
from src.part1.models import Ingredient, Recipe, Supplier, CuisineType, Difficulty, IngredientCategory
from src.part1.max_heap import UrgencyMaxHeap
from src.part1.bst import RecipeBST
from src.part1.supply_graph import SupplyGraph
from src.part1.linked_list import RecipeIngredientLinkedList

# 配置日志（替代简单print，更易调试）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("dataset_generator")

# 提取常量（避免魔法数字，便于维护）
CONST = {
    "MIN_INGREDIENTS": 20,  # 最小食材数（满足约束）
    "MIN_SUPPLIERS": 6,  # 最小供应商数（满足约束）
    "MIN_RECIPES": 15,  # 最小食谱数（满足约束）
    "MIN_SUPPLY_RELATIONS": 30,  # 最小供应关系数（满足约束）
    "MULTI_SUPPLIER_INGS": 3,  # 多供应商食材数（约束）
    "LOW_STOCK_INGS": 5,  # 低库存食材数（约束）
    "LEAD_TIME_RANGE": (3, 14),  # 食材备货周期范围
    "PREP_TIME_RANGE": (10, 90),  # 食谱准备时间范围
    "SERVINGS_RANGE": (2, 8),  # 食谱份数范围
    "ING_QTY_RANGE": (0.2, 3.0),  # 食谱-食材用量范围
    "SUPPLY_COST_RANGE": (2.0, 25.0),  # 供应单价范围
    "RELIABILITY_RANGE": (0.4, 1.0)  # 供应商可靠性范围
}


class DatasetGenerator:
    """
    数据集生成器，严格满足项目约束：
    - 至少15食谱、20食材、6供应商、30供应关系
    - 至少3个菜系、2个难度、5个食材缺库存、3个食材多供应商
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

        # 基础数据集容器
        self.ingredients: List[Ingredient] = []
        self.recipes: List[Recipe] = []
        self.suppliers: List[Supplier] = []
        self.supply_relations: List[Tuple[int, int, float]] = []  # (supplier_id, ingredient_id, cost_per_unit)
        self.recipe_ingredient_relations: List[Tuple[int, int, float]] = []  # (recipe_id, ing_id, quantity)

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

    def generate_ingredients(self, count: int = CONST["MIN_INGREDIENTS"]):
        """
        生成食材（强制≥20个，且前5个食材低于最低库存）
        :param count: 食材数量，自动兜底到最小约束值
        """
        # 兜底校验：确保数量≥约束值
        count = max(count, CONST["MIN_INGREDIENTS"])
        # 扩展食材名池（避免count超过默认20个时索引越界）
        extended_ing_names = self.ingredient_name_pool.copy()
        if count > len(extended_ing_names):
            for i in range(len(extended_ing_names), count):
                extended_ing_names.append(f"ingredient_{i}")


        for i in range(count):
            name = extended_ing_names[i]
            category = random.choice(self.cat_list)

            # 修复：LIQUID枚举已补充，单位判断逻辑优化
            if category in [IngredientCategory.MEAT, IngredientCategory.PRODUCE, IngredientCategory.GRAIN]:
                unit = "kg"
            elif category in [IngredientCategory.LIQUID, IngredientCategory.DAIRY]:
                unit = "L"
            else:  # SPICE
                unit = random.choice(["kg", "g", "L"])

            min_stock = random.randint(5, 20)
            # 强制前N个食材低于最低库存（满足约束）
            if i < CONST["LOW_STOCK_INGS"]:
                current_stock = random.uniform(1, min_stock - 1)  # 改用浮点数更贴近实际
            else:
                current_stock = random.uniform(min_stock, min_stock + 30)

            lead_time = random.randint(*CONST["LEAD_TIME_RANGE"])
            try:
                ingredient = Ingredient(
                    ingredient_id=i,
                    name=name,
                    category=category,
                    unit=unit,
                    current_stock=round(current_stock, 2),
                    minimum_stock=float(min_stock),
                    lead_time=lead_time
                )
                self.ingredients.append(ingredient)
            except Exception as e:
                logger.error(f"生成食材{i}失败：{e}")
                raise

    def generate_suppliers(self, count: int = CONST["MIN_SUPPLIERS"]):
        """
        生成供应商（强制≥6个）
        :param count: 供应商数量，自动兜底到最小约束值
        """
        count = max(count, CONST["MIN_SUPPLIERS"])
        locs = ["Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Chengdu", "Hangzhou"]
        # 扩展地址池（避免count超过6时索引越界）
        extended_locs = locs.copy()
        if count > len(extended_locs):
            for i in range(len(extended_locs), count):
                extended_locs.append(f"City_{i}")

        for i in range(count):
            reliability_score = round(random.uniform(*CONST["RELIABILITY_RANGE"]), 2)
            try:
                supplier = Supplier(
                    supplier_id=i,
                    name=f"Supplier_{i}",
                    location=extended_locs[i],
                    reliability_score=reliability_score
                )
                self.suppliers.append(supplier)
            except ValueError as e:
                logger.error(f"生成供应商{i}失败：{e}")
                raise

    def generate_recipes(self, count: int = CONST["MIN_RECIPES"]):
        """
        生成食谱（强制≥15个，且覆盖≥3个菜系、≥2个难度）
        :param count: 食谱数量，自动兜底到最小约束值
        """
        count = max(count, CONST["MIN_RECIPES"])
        base_recipe_names = [
            "Fried Rice", "Beef Noodle", "Tomato Egg Soup", "Braised Pork",
            "Coconut Curry", "Grilled Steak", "Sushi Roll", "Mapo Tofu",
            "Cream Pasta", "Shrimp Dumpling", "Carrot Salad", "Garlic Bread",
            "Milk Porridge", "Pepper Chicken", "Cheese Omelette"
        ]
        # 扩展食谱名池（避免count超过15时索引越界）
        extended_recipe_names = base_recipe_names.copy()
        if count > len(extended_recipe_names):
            for i in range(len(extended_recipe_names), count):
                extended_recipe_names.append(f"Recipe_{i}")

        logger.info(
            f"Generating {count} recipes (开始生成{count}个食谱) (covering {len(self.cuisine_list)} cuisines - 强制覆盖{len(self.cuisine_list)}个菜系, {len(self.diff_list)} difficulties - {len(self.diff_list)}个难度)")

        # 校验食材是否已生成
        if not self.ingredients:
            raise RuntimeError("请先调用generate_ingredients生成食材")

        for i in range(count):
            name = extended_recipe_names[i]
            # 强制覆盖所有指定菜系（前N个食谱各对应一个菜系）
            cuisine = self.cuisine_list[i] if i < len(self.cuisine_list) else random.choice(self.cuisine_list)
            # 强制覆盖所有指定难度（前N个食谱各对应一个难度）
            difficulty = self.diff_list[i] if i < len(self.diff_list) else random.choice(self.diff_list)

            prep_time = random.randint(*CONST["PREP_TIME_RANGE"])
            servings = random.randint(*CONST["SERVINGS_RANGE"])

            try:
                recipe = Recipe(
                    recipe_id=i,
                    name=name,
                    cuisine_type=cuisine,
                    difficulty=difficulty,
                    prep_time_minutes=prep_time,
                    servings=servings
                )

                # 绑定食材单向链表并记录关联关系
                ll = RecipeIngredientLinkedList()
                ing_num = random.randint(3, 7)
                ing_num = min(ing_num, len(self.ingredients))  # 边界保护
                selected_ings = random.sample(self.ingredients, ing_num)

                for ing in selected_ings:
                    quantity = round(random.uniform(*CONST["ING_QTY_RANGE"]), 1)
                    ll.add_ingredient(ing, quantity)
                    self.recipe_ingredient_relations.append((recipe.recipe_id, ing.ingredient_id, quantity))

                recipe.ingredient_list = ll
                self.recipes.append(recipe)
            except Exception as e:
                logger.error(f"生成食谱{i}失败：{e}")
                raise

    def generate_supply_relationships(self, total: int = CONST["MIN_SUPPLY_RELATIONS"]):
        """
        生成供应关系（强制≥30个，且3个食材有多个供应商）
        :param total: 供应关系总数，自动兜底到最小约束值
        """
        total = max(total, CONST["MIN_SUPPLY_RELATIONS"])

        # 校验供应商/食材是否已生成
        if not self.suppliers:
            raise RuntimeError("请先调用generate_suppliers生成供应商")
        if not self.ingredients:
            raise RuntimeError("请先调用generate_ingredients生成食材")

        ing_ids = [x.ingredient_id for x in self.ingredients]
        sup_ids = [x.supplier_id for x in self.suppliers]

        # 边界校验：确保食材数≥多供应商食材数
        multi_supplier_ing_count = min(CONST["MULTI_SUPPLIER_INGS"], len(ing_ids))
        if multi_supplier_ing_count < CONST["MULTI_SUPPLIER_INGS"]:
            logger.warning(
                f"食材数量不足，仅能为{multi_supplier_ing_count}个食材分配多供应商（要求{CONST['MULTI_SUPPLIER_INGS']}个）")

        # 用集合记录已存在的(sid, iid)，避免重复（O(1)查询）
        existing_supply_pairs = set()

        logger.info(
            f"Generating {total} supply relationships (开始生成{total}个供应关系) (with {multi_supplier_ing_count} ingredients having multiple suppliers - 强制{multi_supplier_ing_count}个食材多供应商)")

        # 步骤1：为指定数量的食材分配多个供应商
        multi_ing_ids = random.sample(ing_ids, multi_supplier_ing_count)
        for ing_id in multi_ing_ids:
            # 每个多供应商食材分配2-4个供应商
            sup_count = random.randint(2, min(4, len(sup_ids)))
            selected_sups = random.sample(sup_ids, sup_count)
            for sid in selected_sups:
                cost = round(random.uniform(*CONST["SUPPLY_COST_RANGE"]), 2)
                if (sid, ing_id) not in existing_supply_pairs:
                    self.supply_relations.append((sid, ing_id, cost))
                    existing_supply_pairs.add((sid, ing_id))

        # 步骤2：填充剩余关系至目标数量（去重）
        while len(self.supply_relations) < total:
            sid = random.choice(sup_ids)
            ing_id = random.choice(ing_ids)
            cost = round(random.uniform(*CONST["SUPPLY_COST_RANGE"]), 2)
            if (sid, ing_id) not in existing_supply_pairs:
                self.supply_relations.append((sid, ing_id, cost))
                existing_supply_pairs.add((sid, ing_id))

    def _get_csv_path(self, filename: str) -> str:
        """辅助方法：拼接CSV文件路径（避免重复代码）"""
        return os.path.join(self.data_dir, filename)

    def write_csv(self):
        """生成5个CSV文件（recipes/ingredients/suppliers/supply_relations/recipe_ingredients）"""
        csv_configs = [
            # (文件名, 表头, 数据生成器)
            (
                "recipes_dataset.csv",
                ["recipe_id", "name", "cuisine_type", "difficulty", "prep_time_minutes", "servings"],
                [
                    [
                        r.recipe_id, r.name, r.cuisine_type.value, r.difficulty.value,
                        r.prep_time_minutes, r.servings
                    ] for r in self.recipes
                ]
            ),
            (
                "ingredients_dataset.csv",
                ["ingredient_id", "name", "category", "unit", "current_stock", "minimum_stock", "lead_time"],
                [
                    [
                        i.ingredient_id, i.name, i.category.value, i.unit,
                        i.current_stock, i.minimum_stock, i.lead_time
                    ] for i in self.ingredients
                ]
            ),
            (
                "suppliers_dataset.csv",
                ["supplier_id", "name", "location", "reliability_score"],
                [
                    [s.supplier_id, s.name, s.location, s.reliability_score]
                    for s in self.suppliers
                ]
            ),
            (
                "supply_relationships_dataset.csv",
                ["supplier_id", "ingredient_id", "cost_per_unit"],
                self.supply_relations
            ),
            (
                "recipe_ingredients.csv",
                ["recipe_id", "ingredient_id", "quantity"],
                self.recipe_ingredient_relations
            )
        ]

        # 批量写入CSV，减少重复代码
        for filename, headers, data in csv_configs:
            path = self._get_csv_path(filename)
            try:
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(data)
            except Exception as e:
                logger.error(f"写入CSV文件{path}失败：{e}")
                raise

    def generate_all_csv(self):
        """生成所有CSV，严格满足项目约束"""
        try:
            self.generate_ingredients()
            self.generate_suppliers()
            self.generate_recipes()
            self.generate_supply_relationships()
            self.write_csv()
        except Exception as e:
            logger.error(f"生成数据集失败：{e}")
            raise

    def load_all_data(self) -> Tuple[RecipeBST, SupplyGraph, UrgencyMaxHeap, Dict[int, Recipe], Dict[int, Supplier]]:
        """
        加载所有CSV数据，从recipe_ingredients.csv构建食材链表
        :return: 食谱BST、供应图、紧急度最大堆、食谱映射表
        """
        required_files = ["ingredients_dataset.csv", "suppliers_dataset.csv", "recipes_dataset.csv",
                          "supply_relationships_dataset.csv", "recipe_ingredients.csv"]
        missing_files = [f for f in required_files if not os.path.exists(self._get_csv_path(f))]
        if missing_files:
            self.generate_all_csv()
        
        # 初始化容器
        ing_map: Dict[int, Ingredient] = {}
        sup_map: Dict[int, Supplier] = {}
        recipe_map: Dict[int, Recipe] = {}
        bst = RecipeBST()
        supply_graph = SupplyGraph()
        heap = UrgencyMaxHeap()

        def read_csv(filename: str) -> List[Dict[str, str]]:
            """读取CSV并返回字典列表，带异常处理"""
            path = self._get_csv_path(filename)
            if not os.path.exists(path):
                raise FileNotFoundError(f"CSV文件不存在：{path}")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return list(csv.DictReader(f))
            except Exception as e:
                raise RuntimeError(f"读取CSV文件{path}失败：{str(e)}")

        try:
            # 1. 加载食材
            for row in read_csv("ingredients_dataset.csv"):
                iid = int(row["ingredient_id"])
                try:
                    category = IngredientCategory(row["category"])
                except ValueError:
                    raise ValueError(f"食材{iid}的分类{row['category']}无效")

                lead_time = int(row.get("lead_time", CONST["LEAD_TIME_RANGE"][0]))
                ing = Ingredient(
                    iid, row["name"], category, row["unit"],
                    float(row["current_stock"]), float(row["minimum_stock"]),
                    lead_time
                )
                ing_map[iid] = ing
                self.ingredients.append(ing)

            # 2. 加载供应商
            for row in read_csv("suppliers_dataset.csv"):
                sid = int(row["supplier_id"])
                sup = Supplier(
                    sid, row["name"], row["location"], float(row["reliability_score"])
                )
                sup_map[sid] = sup
                self.suppliers.append(sup)
                supply_graph.add_supplier(sid)

            # 3. 加载供应关系
            for row in read_csv("supply_relationships_dataset.csv"):
                sid = int(row["supplier_id"])
                iid = int(row["ingredient_id"])
                cost = float(row["cost_per_unit"])
                supply_graph.add_supply_relation(sid, iid, cost)

            # 4. 加载食谱基础信息
            for row in read_csv("recipes_dataset.csv"):
                rid = int(row["recipe_id"])
                try:
                    cuisine = CuisineType(row["cuisine_type"])
                    difficulty = Difficulty(row["difficulty"])
                except ValueError as e:
                    raise ValueError(f"食谱{rid}的枚举值无效：{e}")

                rec = Recipe(
                    rid, row["name"], cuisine, difficulty,
                    int(row["prep_time_minutes"]), int(row["servings"])
                )
                recipe_map[rid] = rec

            # 5. 加载食谱-食材关联，构建链表
            recipe_ing_map: Dict[int, List[Tuple[int, float]]] = {}
            for row in read_csv("recipe_ingredients.csv"):
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
                    else:
                        logger.warning(f"食谱{rid}引用的食材{iid}不存在，跳过")
                rec.ingredient_list = ll
                bst.insert(rec)

            # 6. 统计食材依赖数，填充最大堆
            ing_depend_count: Dict[int, int] = {iid: 0 for iid in ing_map}
            for rec in recipe_map.values():
                for ing, qty in rec.ingredient_list.get_all_ingredients():
                    ing_depend_count[ing.ingredient_id] += 1

            for ing in ing_map.values():
                heap.push(ing, ing_depend_count[ing.ingredient_id])

            return bst, supply_graph, heap, recipe_map, sup_map

        except Exception as e:
            logger.error(f"加载数据失败：{str(e)}")
            raise


# 测试代码（可选，便于验证）
if __name__ == "__main__":
    try:
        generator = DatasetGenerator()
        generator.generate_all_csv()
        # 验证加载
        bst, graph, heap, recipe_map, supplier_map = generator.load_all_data()
        logger.info(
            f"加载完成 - 食谱数：{len(recipe_map)}, 食材数：{len(generator.ingredients)}, "
            f"供应商数：{len(generator.suppliers)}, 供应关系数：{len(generator.supply_relations)}"
        )
    except Exception as e:
        logger.error(f"测试运行失败：{e}")