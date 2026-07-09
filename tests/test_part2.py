import unittest
import tempfile
import shutil
from src.part1.dataset_generator import DatasetGenerator
from src.part1.models import CuisineType, IngredientCategory, Ingredient, Recipe, Difficulty, Supplier
from src.part1.linked_list import RecipeIngredientLinkedList
from src.part2.substitution_graph import SubstitutionGraph
from src.part2.supplier_optimizer import SupplierOptimizer
from src.part2.menu_planner import WeeklyMenuPlanner
from src.part2.benchmark import BenchmarkTester

class TestSubstitutionGraph(unittest.TestCase):
    """测试食材替换图的所有方法及边缘情况"""

    def setUp(self):
        self.sub_graph = SubstitutionGraph()
        self.ing1 = Ingredient(1, "milk", IngredientCategory.DAIRY, "L", 10.0, 5.0, 3)
        self.ing2 = Ingredient(2, "coconut_milk", IngredientCategory.LIQUID, "L", 8.0, 4.0, 5)
        self.ing3 = Ingredient(3, "butter", IngredientCategory.DAIRY, "kg", 5.0, 2.0, 4)
        self.ing4 = Ingredient(4, "cream", IngredientCategory.DAIRY, "L", 6.0, 3.0, 3)
        self.ing5 = Ingredient(5, "beef", IngredientCategory.MEAT, "kg", 3.0, 2.0, 5)
        self.ing6 = Ingredient(6, "pork", IngredientCategory.MEAT, "kg", 4.0, 2.0, 4)

    def test_register_ingredient_normal(self):
        """正常注册食材"""
        self.sub_graph.register_ingredient(self.ing1)
        self.assertIn(1, self.sub_graph.ingredient_map)
        self.assertIn(1, self.sub_graph.sub_edges)

    def test_register_ingredient_none(self):
        """注册None食材"""
        with self.assertRaises((AttributeError, TypeError)):
            self.sub_graph.register_ingredient(None)

    def test_register_ingredient_duplicate(self):
        """重复注册同一食材"""
        self.sub_graph.register_ingredient(self.ing1)
        self.sub_graph.register_ingredient(self.ing1)
        self.assertEqual(len(self.sub_graph.ingredient_map), 1)

    def test_add_substitution_pair_normal(self):
        """正常添加替换对"""
        self.sub_graph.add_substitution_pair(1, 2, 0.9)
        self.assertIn(1, self.sub_graph.sub_edges)
        self.assertIn(2, self.sub_graph.sub_edges)
        self.assertIn((2, 0.9), self.sub_graph.sub_edges[1])
        self.assertIn((1, 0.9), self.sub_graph.sub_edges[2])

    def test_add_substitution_pair_invalid_quality(self):
        """添加无效质量分数"""
        with self.assertRaises(AssertionError):
            self.sub_graph.add_substitution_pair(1, 2, -0.1)
        with self.assertRaises(AssertionError):
            self.sub_graph.add_substitution_pair(1, 2, 1.1)

    def test_add_substitution_pair_same_ingredient(self):
        """添加相同食材的替换对"""
        self.sub_graph.add_substitution_pair(1, 1, 1.0)
        self.assertIn((1, 1.0), self.sub_graph.sub_edges[1])

    def test_build_default_substitution(self):
        """构建默认替换关系"""
        self.sub_graph.build_default_substitution()
        self.assertGreater(len(self.sub_graph.sub_edges), 0)
        self.assertIn(4, self.sub_graph.sub_edges)

    def test_get_all_substitutes_normal(self):
        """正常获取替代食材"""
        self.sub_graph.register_ingredient(self.ing1)
        self.sub_graph.register_ingredient(self.ing2)
        self.sub_graph.add_substitution_pair(1, 2, 0.9)
        subs = self.sub_graph.get_all_substitutes(1)
        self.assertEqual(len(subs), 1)
        self.assertEqual(subs[0][0].ingredient_id, 2)
        self.assertEqual(subs[0][1], 0.9)

    def test_get_all_substitutes_non_existent(self):
        """获取不存在食材的替代"""
        subs = self.sub_graph.get_all_substitutes(999)
        self.assertEqual(subs, [])

    def test_get_all_substitutes_no_registration(self):
        """获取未注册食材的替代"""
        self.sub_graph.add_substitution_pair(1, 2, 0.9)
        subs = self.sub_graph.get_all_substitutes(1)
        self.assertEqual(subs, [])

    def test_get_all_substitutes_sorted(self):
        """替代食材按质量分降序排序"""
        self.sub_graph.register_ingredient(self.ing1)
        self.sub_graph.register_ingredient(self.ing2)
        self.sub_graph.register_ingredient(self.ing3)
        self.sub_graph.add_substitution_pair(1, 2, 0.6)
        self.sub_graph.add_substitution_pair(1, 3, 0.8)
        subs = self.sub_graph.get_all_substitutes(1)
        self.assertEqual(len(subs), 2)
        self.assertGreaterEqual(subs[0][1], subs[1][1])

    def test_check_recipe_with_substitute_feasible(self):
        """替换后库存充足"""
        self.ing2.current_stock = 5.0
        result = self.sub_graph.check_recipe_with_substitute(None, self.ing1, self.ing2, 3.0)
        self.assertTrue(result)

    def test_check_recipe_with_substitute_not_feasible(self):
        """替换后库存不足"""
        self.ing2.current_stock = 1.0
        result = self.sub_graph.check_recipe_with_substitute(None, self.ing1, self.ing2, 3.0)
        self.assertFalse(result)

    def test_rank_substitution_options_normal(self):
        """正常生成排序后的替换方案"""
        self.sub_graph.register_ingredient(self.ing1)
        self.sub_graph.register_ingredient(self.ing2)
        self.sub_graph.register_ingredient(self.ing3)
        self.sub_graph.add_substitution_pair(1, 2, 0.6)
        self.sub_graph.add_substitution_pair(1, 3, 0.8)
        self.ing2.current_stock = 1.0
        self.ing3.current_stock = 5.0
        options = self.sub_graph.rank_substitution_options(None, self.ing1, 3.0)
        self.assertEqual(len(options), 2)
        self.assertTrue(options[0]["can_make"])
        self.assertFalse(options[1]["can_make"])

class TestSupplierOptimizer(unittest.TestCase):
    """测试供应商优化器的所有方法及边缘情况"""

    def setUp(self):
        from src.part1.supply_graph import SupplyGraph
        self.graph = SupplyGraph()
        self.opt = SupplierOptimizer(self.graph)
        self.sup1 = Supplier(1, "Supplier_A", "Beijing", 0.9)
        self.sup2 = Supplier(2, "Supplier_B", "Shanghai", 0.5)
        self.sup3 = Supplier(3, "Supplier_C", "Guangzhou", 0.7)
        self.graph.add_supply_relation(1, 101, 5.0)
        self.graph.add_supply_relation(1, 102, 8.0)
        self.graph.add_supply_relation(2, 101, 6.0)
        self.graph.add_supply_relation(2, 102, 7.0)
        self.graph.add_supply_relation(3, 101, 4.0)
        self.graph.add_supply_relation(3, 103, 9.0)

    def test_add_supplier_normal(self):
        """正常添加供应商"""
        self.opt.add_supplier(self.sup1)
        self.assertIn(1, self.opt.supplier_map)

    def test_add_supplier_none(self):
        """添加None供应商"""
        with self.assertRaises((AttributeError, TypeError)):
            self.opt.add_supplier(None)

    def test_add_supplier_duplicate(self):
        """重复添加同一供应商"""
        self.opt.add_supplier(self.sup1)
        self.opt.add_supplier(self.sup1)
        self.assertEqual(len(self.opt.supplier_map), 1)

    def test_get_min_cost_supplier_set_normal(self):
        """正常获取最小成本供应商组合"""
        self.opt.add_supplier(self.sup1)
        self.opt.add_supplier(self.sup2)
        self.opt.add_supplier(self.sup3)
        ing1 = Ingredient(101, "rice", IngredientCategory.GRAIN, "kg", 10.0, 5.0, 3)
        ing2 = Ingredient(102, "beef", IngredientCategory.MEAT, "kg", 5.0, 3.0, 5)
        ll = RecipeIngredientLinkedList()
        ll.add_ingredient(ing1, 2.0)
        ll.add_ingredient(ing2, 1.0)
        recipe = Recipe(1, "Test Recipe", CuisineType.CHINESE, Difficulty.EASY, 30, 4)
        recipe.ingredient_list = ll
        supplier_map, total_cost = self.opt.get_min_cost_supplier_set(recipe, 0.0)
        self.assertIsNotNone(supplier_map)
        self.assertGreater(total_cost, 0)

    def test_get_min_cost_supplier_set_reliability_filter(self):
        """按可靠性阈值筛选供应商"""
        self.opt.add_supplier(self.sup1)
        self.opt.add_supplier(self.sup2)
        self.opt.add_supplier(self.sup3)
        ing1 = Ingredient(101, "rice", IngredientCategory.GRAIN, "kg", 10.0, 5.0, 3)
        ll = RecipeIngredientLinkedList()
        ll.add_ingredient(ing1, 2.0)
        recipe = Recipe(1, "Test Recipe", CuisineType.CHINESE, Difficulty.EASY, 30, 4)
        recipe.ingredient_list = ll
        supplier_map, total_cost = self.opt.get_min_cost_supplier_set(recipe, 0.8)
        self.assertIsNotNone(supplier_map)
        self.assertEqual(supplier_map[101], 1)

    def test_get_min_cost_supplier_set_no_valid_supplier(self):
        """没有符合条件的供应商（食材完全没有供应关系）"""
        self.opt.add_supplier(self.sup1)
        ing3 = Ingredient(999, "egg", IngredientCategory.PRODUCE, "kg", 20.0, 10.0, 2)
        ll = RecipeIngredientLinkedList()
        ll.add_ingredient(ing3, 2.0)
        recipe = Recipe(1, "Test Recipe", CuisineType.CHINESE, Difficulty.EASY, 30, 4)
        recipe.ingredient_list = ll
        supplier_map, total_cost = self.opt.get_min_cost_supplier_set(recipe, 0.0)
        self.assertIsNone(supplier_map)
        self.assertEqual(total_cost, float("inf"))

    def test_get_min_cost_supplier_set_empty_recipe(self):
        """空食谱"""
        recipe = Recipe(1, "Empty Recipe", CuisineType.CHINESE, Difficulty.EASY, 30, 4)
        recipe.ingredient_list = RecipeIngredientLinkedList()
        supplier_map, total_cost = self.opt.get_min_cost_supplier_set(recipe, 0.0)
        self.assertEqual(supplier_map, {})
        self.assertEqual(total_cost, 0.0)

class TestWeeklyMenuPlanner(unittest.TestCase):
    """测试周菜单规划器的所有方法及边缘情况"""

    def setUp(self):
        from src.part1.bst import RecipeBST
        from src.part1.max_heap import UrgencyMaxHeap
        from src.part1.supply_graph import SupplyGraph
        self.bst = RecipeBST()
        self.heap = UrgencyMaxHeap()
        self.graph = SupplyGraph()
        self.planner = WeeklyMenuPlanner(self.bst, self.heap, self.graph)
        self.ing1 = Ingredient(1, "rice", IngredientCategory.GRAIN, "kg", 2.0, 5.0, 3)
        self.ing2 = Ingredient(2, "beef", IngredientCategory.MEAT, "kg", 10.0, 3.0, 5)

    def test_analyze_menu_normal(self):
        """正常分析菜单"""
        ll = RecipeIngredientLinkedList()
        ll.add_ingredient(self.ing1, 3.0)
        ll.add_ingredient(self.ing2, 1.0)
        recipe = Recipe(1, "Test Recipe", CuisineType.CHINESE, Difficulty.EASY, 30, 4)
        recipe.ingredient_list = ll
        self.bst.insert(recipe)
        self.heap.push(self.ing1, 5)
        self.heap.push(self.ing2, 3)
        shortage, procure_plan = self.planner.analyze_menu([recipe])
        self.assertEqual(len(shortage), 1)
        self.assertEqual(shortage[0].ingredient_id, 1)

    def test_analyze_menu_empty(self):
        """分析空菜单"""
        shortage, procure_plan = self.planner.analyze_menu([])
        self.assertEqual(shortage, [])
        self.assertEqual(procure_plan, [])

    def test_analyze_menu_all_feasible(self):
        """所有食谱都可行"""
        self.ing1.current_stock = 10.0
        ll = RecipeIngredientLinkedList()
        ll.add_ingredient(self.ing1, 3.0)
        ll.add_ingredient(self.ing2, 1.0)
        recipe = Recipe(1, "Test Recipe", CuisineType.CHINESE, Difficulty.EASY, 30, 4)
        recipe.ingredient_list = ll
        self.bst.insert(recipe)
        self.heap.push(self.ing1, 5)
        shortage, procure_plan = self.planner.analyze_menu([recipe])
        self.assertEqual(shortage, [])
        self.assertEqual(procure_plan, [])

    def test_generate_weekly_menu(self):
        """生成本周菜单"""
        self.ing1.current_stock = 10.0
        ll = RecipeIngredientLinkedList()
        ll.add_ingredient(self.ing1, 3.0)
        recipe = Recipe(1, "Test Recipe", CuisineType.CHINESE, Difficulty.EASY, 30, 4)
        recipe.ingredient_list = ll
        self.bst.insert(recipe)
        
        menu = self.planner.generate_weekly_menu()
        self.assertEqual(len(menu), 7)
        for day_plan in menu:
            self.assertIn('day', day_plan)
            self.assertIn('recipe', day_plan)
            self.assertIn('feasible', day_plan)

    def test_generate_weekly_menu_empty_bst(self):
        """空BST生成本周菜单"""
        menu = self.planner.generate_weekly_menu()
        self.assertEqual(len(menu), 7)
        for day_plan in menu:
            self.assertIsNone(day_plan['recipe'])
            self.assertIsNone(day_plan['feasible'])

    def test_generate_next_week_menu(self):
        """生成下周菜单"""
        self.ing1.current_stock = 10.0
        ll = RecipeIngredientLinkedList()
        ll.add_ingredient(self.ing1, 3.0)
        recipe = Recipe(1, "Test Recipe", CuisineType.CHINESE, Difficulty.EASY, 30, 4)
        recipe.ingredient_list = ll
        self.bst.insert(recipe)
        
        menu = self.planner.generate_next_week_menu()
        self.assertEqual(len(menu), 7)
        for day_plan in menu:
            self.assertIn('week_offset', day_plan)
            self.assertEqual(day_plan['week_offset'], 1)

    def test_get_all_recipes(self):
        """获取所有食谱"""
        self.ing1.current_stock = 10.0
        ll = RecipeIngredientLinkedList()
        ll.add_ingredient(self.ing1, 3.0)
        recipe = Recipe(1, "Test Recipe", CuisineType.CHINESE, Difficulty.EASY, 30, 4)
        recipe.ingredient_list = ll
        self.bst.insert(recipe)
        
        recipes = self.planner.get_all_recipes()
        self.assertEqual(len(recipes), 1)
        self.assertEqual(recipes[0].name, "Test Recipe")

    def test_get_feasible_recipes(self):
        """获取可行食谱"""
        self.ing1.current_stock = 10.0
        ll = RecipeIngredientLinkedList()
        ll.add_ingredient(self.ing1, 3.0)
        recipe = Recipe(1, "Test Recipe", CuisineType.CHINESE, Difficulty.EASY, 30, 4)
        recipe.ingredient_list = ll
        self.bst.insert(recipe)
        
        feasible = self.planner.get_feasible_recipes()
        self.assertEqual(len(feasible), 1)

    def test_get_recipe_feasibility(self):
        """获取食谱可行性"""
        ll = RecipeIngredientLinkedList()
        ll.add_ingredient(self.ing1, 3.0)
        recipe = Recipe(1, "Test Recipe", CuisineType.CHINESE, Difficulty.EASY, 30, 4)
        recipe.ingredient_list = ll
        
        result = self.planner.get_recipe_feasibility(recipe)
        self.assertEqual(result['recipe'], recipe)
        self.assertFalse(result['feasible'])
        self.assertEqual(len(result['missing']), 1)

class TestBenchmarkTester(unittest.TestCase):
    """测试性能基准测试器"""

    def test_run_benchmark(self):
        """运行性能基准测试"""
        tester = BenchmarkTester()
        tester.run_benchmark()
        self.assertEqual(len(tester.results["bst_search"]), len(tester.scales))
        self.assertEqual(len(tester.results["supplier_opt"]), len(tester.scales))

class TestIntegration(unittest.TestCase):
    """集成测试：验证Part2整体流程"""

    @classmethod
    def setUpClass(cls):
        cls.test_data_dir = tempfile.mkdtemp()
        gen = DatasetGenerator(data_dir=cls.test_data_dir)
        gen.generate_all_csv()
        cls.bst, cls.supply_graph, cls.heap, cls.recipe_map, cls.supplier_map = gen.load_all_data()
        cls.sub_graph = SubstitutionGraph()
        cls.sub_graph.build_default_substitution()
        for ing in gen.ingredients:
            cls.sub_graph.register_ingredient(ing)
        cls.opt = SupplierOptimizer(cls.supply_graph)
        for sup in cls.supplier_map.values():
            cls.opt.add_supplier(sup)
        cls.sample_recipe = list(cls.recipe_map.values())[0]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_data_dir, ignore_errors=True)

    def test_substitution_search(self):
        """测试食材替换图可查询替代食材"""
        subs = self.sub_graph.get_all_substitutes(4)
        self.assertGreater(len(subs), 0)

    def test_min_cost_supplier_calc(self):
        """测试最优供应商成本计算正常"""
        for recipe in self.recipe_map.values():
            supplier_map, total_cost = self.opt.get_min_cost_supplier_set(recipe, 0.0)
            if supplier_map is not None:
                self.assertGreater(total_cost, 0)
                return
        self.fail("没有找到所有食材都有供应商的食谱")

    def test_menu_planner(self):
        """测试菜单规划器"""
        planner = WeeklyMenuPlanner(self.bst, self.heap, self.supply_graph)
        test_menu = list(self.recipe_map.values())[:3]
        shortage, procure_plan = planner.analyze_menu(test_menu)
        self.assertIsInstance(shortage, list)
        self.assertIsInstance(procure_plan, list)

    def test_benchmark_plot(self):
        """测试性能基准图表生成"""
        import os
        tester = BenchmarkTester()
        tester.run_benchmark()
        self.assertTrue(os.path.exists("./reports/benchmark_plot.png"))

if __name__ == "__main__":
    unittest.main()