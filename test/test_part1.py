import unittest
import os
from src.part1.dataset_generator import DatasetGenerator
from src.part1.models import CuisineType, Difficulty, Ingredient


class TestPart1DataStructures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 确保数据集目录存在
        os.makedirs("data", exist_ok=True)
        # 生成符合约束的数据集
        gen = DatasetGenerator()
        gen.generate_all_csv()
        cls.bst, cls.supply_graph, cls.heap, cls.recipe_map = gen.load_all_data()
        cls.all_recipes = cls.bst.in_order()
        cls.all_ingredients = list(gen.ingredients)

    def test_dataset_constraints(self):
        """验证数据集满足所有强制约束"""
        # 1. 食谱数量≥15
        self.assertGreaterEqual(len(self.all_recipes), 15)
        # 2. 食材数量≥20
        self.assertGreaterEqual(len(self.all_ingredients), 20)
        # 3. 至少3个菜系
        cuisines = set([r.cuisine_type for r in self.all_recipes])
        self.assertGreaterEqual(len(cuisines), 3)
        # 4. 至少2个难度
        difficulties = set([r.difficulty for r in self.all_recipes])
        self.assertGreaterEqual(len(difficulties), 2)
        # 5. 至少5个食材低于最低库存
        shortage_ings = [ing for ing in self.all_ingredients if ing.stock_shortage() > 0]
        self.assertGreaterEqual(len(shortage_ings), 5)
        # 6. 至少3个食材有多个供应商
        multi_sup_ings = 0
        for ing_id in self.supply_graph.ingredient_to_suppliers:
            suppliers = self.supply_graph.get_suppliers_for_ingredient(ing_id)
            if len(suppliers) > 1:
                multi_sup_ings += 1
        self.assertGreaterEqual(multi_sup_ings, 3)

    def test_bst_in_order_alphabet(self):
        """测试BST中序遍历字母升序"""
        names = [r.name.lower() for r in self.all_recipes]
        sorted_names = sorted(names)
        self.assertEqual(names, sorted_names)

    def test_linked_list_length_match(self):
        """每个食谱链表长度匹配CSV中的食材数量"""
        # 读取recipe_ingredients.csv的食材数量
        recipe_ing_count = {}
        with open("data/recipe_ingredients.csv", "r", encoding="utf-8") as f:
            next(f)  # 跳过表头
            for line in f:
                rid = int(line.split(",")[0])
                recipe_ing_count[rid] = recipe_ing_count.get(rid, 0) + 1

        # 验证链表长度
        for rec in self.all_recipes:
            self.assertEqual(rec.ingredient_list.size, recipe_ing_count.get(rec.recipe_id, 0))

    def test_max_heap_highest_urgency_first(self):
        """堆弹出最高紧急度食材"""
        top1 = self.heap.pop_highest()
        top2 = self.heap.pop_highest()
        if top1 and top2:
            self.assertGreaterEqual(top1[0], top2[0])
            # 放回堆
            self.heap.push(top1[1], 0)
            self.heap.push(top2[1], 0)

    def test_supply_graph_get_ingredient_suppliers(self):
        """供应图可正确查询食材供应商"""
        all_ing_ids = list(self.supply_graph.ingredient_to_suppliers.keys())
        self.assertGreater(len(all_ing_ids), 0)
        for iid in all_ing_ids:
            suppliers = self.supply_graph.get_suppliers_for_ingredient(iid)
            self.assertGreater(len(suppliers), 0)


if __name__ == "__main__":
    unittest.main()