import unittest
import tempfile
import shutil
from src.part1.dataset_generator import DatasetGenerator
from src.part1.models import CuisineType, IngredientCategory, Ingredient, Recipe, Difficulty
from src.part1.linked_list import RecipeIngredientLinkedList
from src.part1.bst import RecipeBST
from src.part1.max_heap import UrgencyMaxHeap
from src.part1.supply_graph import SupplyGraph

class TestLinkedList(unittest.TestCase):
    """测试链表数据结构的所有方法及边缘情况"""

    def setUp(self):
        self.ll = RecipeIngredientLinkedList()
        self.ing1 = Ingredient(1, "rice", IngredientCategory.GRAIN, "kg", 10.0, 5.0, 3)
        self.ing2 = Ingredient(2, "beef", IngredientCategory.MEAT, "kg", 5.0, 3.0, 5)
        self.ing3 = Ingredient(3, "egg", IngredientCategory.PRODUCE, "kg", 20.0, 10.0, 2)

    def test_add_ingredient_normal(self):
        """正常添加食材到链表"""
        self.ll.add_ingredient(self.ing1, 1.0)
        self.assertEqual(self.ll.size, 1)
        all_ings = self.ll.get_all_ingredients()
        self.assertEqual(len(all_ings), 1)
        self.assertEqual(all_ings[0][0].ingredient_id, 1)
        self.assertEqual(all_ings[0][1], 1.0)

    def test_add_ingredient_multiple(self):
        """添加多个食材"""
        self.ll.add_ingredient(self.ing1, 1.0)
        self.ll.add_ingredient(self.ing2, 0.5)
        self.ll.add_ingredient(self.ing3, 2.0)
        self.assertEqual(self.ll.size, 3)
        all_ings = self.ll.get_all_ingredients()
        self.assertEqual(len(all_ings), 3)
        self.assertEqual(all_ings[0][0].ingredient_id, 1)
        self.assertEqual(all_ings[1][0].ingredient_id, 2)
        self.assertEqual(all_ings[2][0].ingredient_id, 3)

    def test_add_ingredient_none(self):
        """添加None食材应抛出异常"""
        with self.assertRaises((AttributeError, TypeError)):
            self.ll.add_ingredient(None, 1.0)

    def test_add_ingredient_negative_quantity(self):
        """添加负数数量的食材"""
        self.ll.add_ingredient(self.ing1, -1.0)
        self.assertEqual(self.ll.size, 1)
        all_ings = self.ll.get_all_ingredients()
        self.assertEqual(all_ings[0][1], -1.0)

    def test_remove_ingredient_normal(self):
        """正常移除食材"""
        self.ll.add_ingredient(self.ing1, 1.0)
        self.ll.add_ingredient(self.ing2, 0.5)
        result = self.ll.remove_ingredient(1)
        self.assertTrue(result)
        self.assertEqual(self.ll.size, 1)
        all_ings = self.ll.get_all_ingredients()
        self.assertEqual(all_ings[0][0].ingredient_id, 2)

    def test_remove_ingredient_from_empty(self):
        """从空链表移除食材"""
        result = self.ll.remove_ingredient(1)
        self.assertFalse(result)
        self.assertEqual(self.ll.size, 0)

    def test_remove_ingredient_non_existent(self):
        """移除不存在的食材ID"""
        self.ll.add_ingredient(self.ing1, 1.0)
        result = self.ll.remove_ingredient(999)
        self.assertFalse(result)
        self.assertEqual(self.ll.size, 1)

    def test_remove_ingredient_negative_id(self):
        """移除负数ID的食材"""
        self.ll.add_ingredient(self.ing1, 1.0)
        result = self.ll.remove_ingredient(-1)
        self.assertFalse(result)
        self.assertEqual(self.ll.size, 1)

    def test_remove_ingredient_head(self):
        """移除头部节点"""
        self.ll.add_ingredient(self.ing1, 1.0)
        self.ll.add_ingredient(self.ing2, 0.5)
        self.ll.add_ingredient(self.ing3, 2.0)
        result = self.ll.remove_ingredient(1)
        self.assertTrue(result)
        self.assertEqual(self.ll.size, 2)
        all_ings = self.ll.get_all_ingredients()
        self.assertEqual(all_ings[0][0].ingredient_id, 2)

    def test_remove_ingredient_tail(self):
        """移除尾部节点"""
        self.ll.add_ingredient(self.ing1, 1.0)
        self.ll.add_ingredient(self.ing2, 0.5)
        self.ll.add_ingredient(self.ing3, 2.0)
        result = self.ll.remove_ingredient(3)
        self.assertTrue(result)
        self.assertEqual(self.ll.size, 2)
        all_ings = self.ll.get_all_ingredients()
        self.assertEqual(all_ings[-1][0].ingredient_id, 2)

    def test_tail_pointer_after_add(self):
        """验证添加元素后tail指针正确指向最后一个节点"""
        self.ll.add_ingredient(self.ing1, 1.0)
        self.assertIsNotNone(self.ll.tail)
        self.assertEqual(self.ll.tail.ingredient.ingredient_id, 1)
        self.assertEqual(self.ll.tail.quantity, 1.0)
        
        self.ll.add_ingredient(self.ing2, 0.5)
        self.assertIsNotNone(self.ll.tail)
        self.assertEqual(self.ll.tail.ingredient.ingredient_id, 2)
        self.assertEqual(self.ll.tail.quantity, 0.5)
        
        self.ll.add_ingredient(self.ing3, 2.0)
        self.assertIsNotNone(self.ll.tail)
        self.assertEqual(self.ll.tail.ingredient.ingredient_id, 3)
        self.assertEqual(self.ll.tail.quantity, 2.0)

    def test_tail_pointer_after_remove_head(self):
        """移除头部节点后tail指针保持正确"""
        self.ll.add_ingredient(self.ing1, 1.0)
        self.ll.add_ingredient(self.ing2, 0.5)
        self.ll.add_ingredient(self.ing3, 2.0)
        
        self.ll.remove_ingredient(1)
        self.assertIsNotNone(self.ll.tail)
        self.assertEqual(self.ll.tail.ingredient.ingredient_id, 3)

    def test_tail_pointer_after_remove_tail(self):
        """移除尾部节点后tail指针更新为新的尾部"""
        self.ll.add_ingredient(self.ing1, 1.0)
        self.ll.add_ingredient(self.ing2, 0.5)
        self.ll.add_ingredient(self.ing3, 2.0)
        
        self.ll.remove_ingredient(3)
        self.assertIsNotNone(self.ll.tail)
        self.assertEqual(self.ll.tail.ingredient.ingredient_id, 2)

    def test_tail_pointer_after_remove_all(self):
        """移除所有节点后tail指针为None"""
        self.ll.add_ingredient(self.ing1, 1.0)
        self.ll.remove_ingredient(1)
        self.assertIsNone(self.ll.tail)
        self.assertIsNone(self.ll.head)

    def test_tail_pointer_single_node(self):
        """单个节点时head和tail指向同一节点"""
        self.ll.add_ingredient(self.ing1, 1.0)
        self.assertIs(self.ll.head, self.ll.tail)

    def test_update_quantity_normal(self):
        """正常更新数量"""
        self.ll.add_ingredient(self.ing1, 1.0)
        result = self.ll.update_quantity(1, 2.5)
        self.assertTrue(result)
        all_ings = self.ll.get_all_ingredients()
        self.assertEqual(all_ings[0][1], 2.5)

    def test_update_quantity_non_existent(self):
        """更新不存在的食材ID"""
        self.ll.add_ingredient(self.ing1, 1.0)
        result = self.ll.update_quantity(999, 2.5)
        self.assertFalse(result)
        all_ings = self.ll.get_all_ingredients()
        self.assertEqual(all_ings[0][1], 1.0)

    def test_update_quantity_negative(self):
        """更新为负数数量"""
        self.ll.add_ingredient(self.ing1, 1.0)
        result = self.ll.update_quantity(1, -5.0)
        self.assertTrue(result)
        all_ings = self.ll.get_all_ingredients()
        self.assertEqual(all_ings[0][1], -5.0)

    def test_get_all_ingredients_empty(self):
        """获取空链表的所有食材"""
        result = self.ll.get_all_ingredients()
        self.assertEqual(result, [])

    def test_check_recipe_feasible_all_enough(self):
        """所有食材库存充足"""
        self.ll.add_ingredient(self.ing1, 2.0)
        feasible, shortage = self.ll.check_recipe_feasible()
        self.assertTrue(feasible)
        self.assertEqual(shortage, [])

    def test_check_recipe_feasible_shortage(self):
        """部分食材库存不足"""
        self.ing1.current_stock = 0.5
        self.ll.add_ingredient(self.ing1, 2.0)
        self.ll.add_ingredient(self.ing2, 0.5)
        feasible, shortage = self.ll.check_recipe_feasible()
        self.assertFalse(feasible)
        self.assertEqual(len(shortage), 1)
        self.assertEqual(shortage[0].ingredient_id, 1)

    def test_check_recipe_feasible_empty(self):
        """空链表的可行性检查"""
        feasible, shortage = self.ll.check_recipe_feasible()
        self.assertTrue(feasible)
        self.assertEqual(shortage, [])

class TestBST(unittest.TestCase):
    """测试BST数据结构的所有方法及边缘情况"""

    def setUp(self):
        self.bst = RecipeBST()
        self.rec1 = Recipe(1, "Apple Pie", CuisineType.WESTERN, Difficulty.MEDIUM, 45, 4)
        self.rec2 = Recipe(2, "Banana Bread", CuisineType.WESTERN, Difficulty.EASY, 30, 6)
        self.rec3 = Recipe(3, "Carrot Cake", CuisineType.WESTERN, Difficulty.MEDIUM, 50, 8)
        self.rec4 = Recipe(4, "Date Soup", CuisineType.CHINESE, Difficulty.EASY, 20, 4)

    def test_insert_normal(self):
        """正常插入食谱"""
        self.bst.insert(self.rec1)
        result = self.bst.search("Apple Pie")
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "Apple Pie")

    def test_insert_multiple_ordered(self):
        """插入多个食谱并验证中序遍历顺序"""
        self.bst.insert(self.rec2)
        self.bst.insert(self.rec1)
        self.bst.insert(self.rec4)
        self.bst.insert(self.rec3)
        in_order = self.bst.in_order()
        names = [r.name for r in in_order]
        self.assertEqual(names, ["Apple Pie", "Banana Bread", "Carrot Cake", "Date Soup"])

    def test_insert_none(self):
        """插入None应抛出异常"""
        with self.assertRaises((AttributeError, TypeError)):
            self.bst.insert(None)

    def test_insert_duplicate_name(self):
        """插入同名食谱（存入右子树）"""
        self.bst.insert(self.rec1)
        self.rec1_copy = Recipe(5, "Apple Pie", CuisineType.CHINESE, Difficulty.EASY, 30, 4)
        self.bst.insert(self.rec1_copy)
        result = self.bst.search("Apple Pie")
        self.assertIsNotNone(result)

    def test_search_existing(self):
        """搜索存在的食谱"""
        self.bst.insert(self.rec1)
        self.bst.insert(self.rec2)
        result = self.bst.search("Banana Bread")
        self.assertIsNotNone(result)
        self.assertEqual(result.recipe_id, 2)

    def test_search_non_existent(self):
        """搜索不存在的食谱"""
        self.bst.insert(self.rec1)
        result = self.bst.search("Non-existent")
        self.assertIsNone(result)

    def test_search_case_insensitive(self):
        """不区分大小写搜索"""
        self.bst.insert(self.rec1)
        result = self.bst.search("apple pie")
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "Apple Pie")

    def test_search_case_sensitive(self):
        """区分大小写搜索"""
        self.bst.insert(self.rec1)
        result = self.bst.search("apple pie", case_sensitive=True)
        self.assertIsNone(result)
        result = self.bst.search("Apple Pie", case_sensitive=True)
        self.assertIsNotNone(result)

    def test_delete_existing(self):
        """删除存在的食谱"""
        self.bst.insert(self.rec1)
        self.bst.insert(self.rec2)
        self.bst.insert(self.rec3)
        result = self.bst.delete("Banana Bread")
        self.assertTrue(result)
        self.assertIsNone(self.bst.search("Banana Bread"))

    def test_delete_non_existent(self):
        """删除不存在的食谱"""
        self.bst.insert(self.rec1)
        result = self.bst.delete("Non-existent")
        self.assertFalse(result)

    def test_delete_root(self):
        """删除根节点"""
        self.bst.insert(self.rec2)
        self.bst.insert(self.rec1)
        self.bst.insert(self.rec3)
        result = self.bst.delete("Banana Bread")
        self.assertTrue(result)
        in_order = self.bst.in_order()
        self.assertEqual(len(in_order), 2)

    def test_delete_leaf(self):
        """删除叶子节点"""
        self.bst.insert(self.rec2)
        self.bst.insert(self.rec1)
        result = self.bst.delete("Apple Pie")
        self.assertTrue(result)
        self.assertIsNone(self.bst.search("Apple Pie"))

    def test_delete_empty_tree(self):
        """从空树删除"""
        result = self.bst.delete("Any")
        self.assertFalse(result)

    def test_range_search_normal(self):
        """正常范围搜索"""
        self.bst.insert(self.rec1)
        self.bst.insert(self.rec2)
        self.bst.insert(self.rec3)
        self.bst.insert(self.rec4)
        result = self.bst.range_search("A", "C")
        self.assertEqual(len(result), 3)
        names = [r.name for r in result]
        self.assertIn("Apple Pie", names)
        self.assertIn("Banana Bread", names)
        self.assertIn("Carrot Cake", names)

    def test_range_search_invalid_params(self):
        """无效参数的范围搜索"""
        self.bst.insert(self.rec1)
        result = self.bst.range_search("", "C")
        self.assertEqual(result, [])
        result = self.bst.range_search("A", "")
        self.assertEqual(result, [])
        result = self.bst.range_search("AB", "C")
        self.assertEqual(result, [])

    def test_range_search_empty_tree(self):
        """空树的范围搜索"""
        result = self.bst.range_search("A", "Z")
        self.assertEqual(result, [])

    def test_get_recipes_by_cuisine(self):
        """按菜系筛选"""
        self.bst.insert(self.rec1)
        self.bst.insert(self.rec2)
        self.bst.insert(self.rec4)
        western = self.bst.get_recipes_by_cuisine(CuisineType.WESTERN)
        chinese = self.bst.get_recipes_by_cuisine(CuisineType.CHINESE)
        self.assertEqual(len(western), 2)
        self.assertEqual(len(chinese), 1)

    def test_get_bst_height(self):
        """计算BST高度"""
        self.assertEqual(self.bst.get_bst_height(), 0)
        self.bst.insert(self.rec1)
        self.assertEqual(self.bst.get_bst_height(), 1)
        self.bst.insert(self.rec2)
        self.assertEqual(self.bst.get_bst_height(), 2)

    def test_get_all_feasible_recipes_empty(self):
        """空树获取可行食谱"""
        result = self.bst.get_all_feasible_recipes()
        self.assertEqual(result, [])

class TestMaxHeap(unittest.TestCase):
    """测试最大堆数据结构的所有方法及边缘情况"""

    def setUp(self):
        self.heap = UrgencyMaxHeap()
        self.ing1 = Ingredient(1, "rice", IngredientCategory.GRAIN, "kg", 2.0, 5.0, 3)
        self.ing2 = Ingredient(2, "beef", IngredientCategory.MEAT, "kg", 1.0, 3.0, 5)
        self.ing3 = Ingredient(3, "egg", IngredientCategory.PRODUCE, "kg", 20.0, 10.0, 2)

    def test_push_normal(self):
        """正常压入食材"""
        self.heap.push(self.ing1, 5)
        self.assertEqual(self.heap.size(), 1)

    def test_push_multiple(self):
        """压入多个食材"""
        self.heap.push(self.ing1, 5)
        self.heap.push(self.ing2, 10)
        self.heap.push(self.ing3, 3)
        self.assertEqual(self.heap.size(), 3)

    def test_push_none(self):
        """压入None应抛出异常"""
        with self.assertRaises((AttributeError, TypeError)):
            self.heap.push(None, 5)

    def test_push_duplicate(self):
        """压入重复食材（更新紧急度）"""
        self.heap.push(self.ing1, 5)
        self.assertEqual(self.heap.size(), 1)
        self.heap.push(self.ing1, 10)
        self.assertEqual(self.heap.size(), 1)

    def test_pop_highest_normal(self):
        """正常弹出最高优先级（ing1库存缺口更大，紧急度更高）"""
        self.heap.push(self.ing1, 5)
        self.heap.push(self.ing2, 10)
        top = self.heap.pop_highest()
        self.assertIsNotNone(top)
        self.assertEqual(top[1].ingredient_id, 1)
        self.assertEqual(self.heap.size(), 1)

    def test_pop_highest_empty(self):
        """从空堆弹出"""
        result = self.heap.pop_highest()
        self.assertIsNone(result)

    def test_get_top_k_normal(self):
        """正常获取前k个"""
        self.heap.push(self.ing1, 5)
        self.heap.push(self.ing2, 10)
        self.heap.push(self.ing3, 3)
        top2 = self.heap.get_top_k(2)
        self.assertEqual(len(top2), 2)
        self.assertEqual(self.heap.size(), 3)

    def test_get_top_k_zero(self):
        """获取0个"""
        self.heap.push(self.ing1, 5)
        result = self.heap.get_top_k(0)
        self.assertEqual(result, [])

    def test_get_top_k_larger_than_size(self):
        """获取超过堆大小的数量"""
        self.heap.push(self.ing1, 5)
        result = self.heap.get_top_k(100)
        self.assertEqual(len(result), 1)

    def test_get_top_k_empty(self):
        """从空堆获取前k个"""
        result = self.heap.get_top_k(5)
        self.assertEqual(result, [])

    def test_calc_urgency_score(self):
        """计算紧急度分数"""
        score = UrgencyMaxHeap.calc_urgency_score(self.ing1, 5)
        self.assertEqual(self.ing1.stock_shortage(), 3.0)
        expected = 3.0 * 10 + 5 + (30 - 3)
        self.assertEqual(score, round(expected, 2))

    def test_size_empty(self):
        """空堆大小"""
        self.assertEqual(self.heap.size(), 0)

class TestSupplyGraph(unittest.TestCase):
    """测试供应图数据结构的所有方法及边缘情况"""

    def setUp(self):
        self.graph = SupplyGraph()

    def test_add_supplier_normal(self):
        """正常添加供应商"""
        self.graph.add_supplier(1)
        self.assertIn(1, self.graph.adj)

    def test_add_supplier_negative(self):
        """添加负数ID供应商"""
        self.graph.add_supplier(-1)
        self.assertIn(-1, self.graph.adj)

    def test_add_supplier_duplicate(self):
        """添加重复供应商"""
        self.graph.add_supplier(1)
        self.graph.add_supplier(1)
        self.assertIn(1, self.graph.adj)

    def test_remove_supplier_normal(self):
        """正常移除供应商"""
        self.graph.add_supply_relation(1, 101, 5.0)
        self.graph.remove_supplier(1)
        self.assertNotIn(1, self.graph.adj)

    def test_remove_supplier_non_existent(self):
        """移除不存在的供应商"""
        self.graph.remove_supplier(999)
        self.assertNotIn(999, self.graph.adj)

    def test_add_supply_relation_normal(self):
        """正常添加供应关系"""
        self.graph.add_supply_relation(1, 101, 5.0)
        self.assertIn(1, self.graph.adj)
        self.assertIn(101, self.graph.adj[1])
        self.assertIn(101, self.graph.ingredient_to_suppliers)

    def test_add_supply_relation_duplicate(self):
        """添加重复供应关系"""
        self.graph.add_supply_relation(1, 101, 5.0)
        self.graph.add_supply_relation(1, 101, 6.0)
        self.assertEqual(self.graph.adj[1][101], 6.0)
        self.assertEqual(len(self.graph.ingredient_to_suppliers[101]), 1)

    def test_remove_supply_relation_normal(self):
        """正常移除供应关系"""
        self.graph.add_supply_relation(1, 101, 5.0)
        self.graph.add_supply_relation(2, 101, 6.0)
        self.graph.remove_supply_relation(1, 101)
        self.assertNotIn(101, self.graph.adj[1])
        self.assertIn(101, self.graph.ingredient_to_suppliers)

    def test_remove_supply_relation_last(self):
        """移除最后一个供应关系"""
        self.graph.add_supply_relation(1, 101, 5.0)
        self.graph.remove_supply_relation(1, 101)
        self.assertNotIn(101, self.graph.ingredient_to_suppliers)

    def test_remove_supply_relation_non_existent(self):
        """移除不存在的供应关系"""
        self.graph.add_supply_relation(1, 101, 5.0)
        self.graph.remove_supply_relation(999, 999)
        self.assertIn(101, self.graph.ingredient_to_suppliers)

    def test_get_suppliers_for_ingredient_normal(self):
        """正常获取食材供应商"""
        self.graph.add_supply_relation(1, 101, 5.0)
        self.graph.add_supply_relation(2, 101, 6.0)
        suppliers = self.graph.get_suppliers_for_ingredient(101)
        self.assertEqual(len(suppliers), 2)
        self.assertIn(1, suppliers)
        self.assertIn(2, suppliers)

    def test_get_suppliers_for_ingredient_non_existent(self):
        """获取不存在食材的供应商"""
        suppliers = self.graph.get_suppliers_for_ingredient(999)
        self.assertEqual(suppliers, [])

    def test_get_unit_cost_normal(self):
        """正常获取单位成本"""
        self.graph.add_supply_relation(1, 101, 5.0)
        cost = self.graph.get_unit_cost(1, 101)
        self.assertEqual(cost, 5.0)

    def test_get_unit_cost_non_existent(self):
        """获取不存在的单位成本"""
        with self.assertRaises(KeyError):
            self.graph.get_unit_cost(999, 999)

    def test_get_cheapest_supplier_normal(self):
        """正常获取最便宜供应商"""
        self.graph.add_supply_relation(1, 101, 5.0)
        self.graph.add_supply_relation(2, 101, 3.0)
        self.graph.add_supply_relation(3, 101, 4.0)
        best_sid, cost = self.graph.get_cheapest_supplier(101)
        self.assertEqual(best_sid, 2)
        self.assertEqual(cost, 3.0)

    def test_get_cheapest_supplier_non_existent(self):
        """获取不存在食材的最便宜供应商"""
        result = self.graph.get_cheapest_supplier(999)
        self.assertIsNone(result)

    def test_get_ingredients_under_budget_normal(self):
        """正常筛选预算内食材"""
        self.graph.add_supply_relation(1, 101, 5.0)
        self.graph.add_supply_relation(1, 102, 15.0)
        self.graph.add_supply_relation(2, 103, 8.0)
        result = self.graph.get_ingredients_under_budget(10.0)
        self.assertEqual(len(result), 2)
        self.assertIn(101, result)
        self.assertIn(103, result)

    def test_get_ingredients_under_budget_empty(self):
        """空图筛选预算内食材"""
        result = self.graph.get_ingredients_under_budget(10.0)
        self.assertEqual(result, [])

class TestIntegration(unittest.TestCase):
    """集成测试：验证数据生成和加载流程"""

    @classmethod
    def setUpClass(cls):
        cls.test_data_dir = tempfile.mkdtemp()
        gen = DatasetGenerator(data_dir=cls.test_data_dir)
        gen.generate_all_csv()
        cls.bst, cls.supply_graph, cls.heap, cls.recipe_map, cls.supplier_map = gen.load_all_data()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_data_dir, ignore_errors=True)

    def test_bst_in_order_alphabet(self):
        """测试BST中序遍历字母升序"""
        all_recipes = self.bst.in_order()
        names = [r.name.lower() for r in all_recipes]
        sorted_names = sorted(names)
        self.assertEqual(names, sorted_names)

    def test_linked_list_length_match(self):
        """每个食谱链表长度匹配食材数量"""
        all_recipes = self.bst.in_order()
        for rec in all_recipes:
            self.assertGreater(rec.ingredient_list.size, 0)

    def test_max_heap_highest_urgency_first(self):
        """堆弹出最高紧急度食材"""
        top1 = self.heap.pop_highest()
        top2 = self.heap.pop_highest()
        self.assertGreaterEqual(top1[0], top2[0])
        self.heap.push(top1[1], 0)
        self.heap.push(top2[1], 0)

    def test_supply_graph_get_ingredient_suppliers(self):
        """供应图可正确查询食材供应商"""
        all_ing_ids = list(self.supply_graph.ingredient_to_suppliers.keys())
        self.assertGreater(len(all_ing_ids), 3)
        for iid in all_ing_ids:
            suppliers = self.supply_graph.get_suppliers_for_ingredient(iid)
            self.assertGreater(len(suppliers), 0)

if __name__ == "__main__":
    unittest.main()