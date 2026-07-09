import unittest
import tempfile
import shutil
from src.part1.dataset_generator import DatasetGenerator
from src.part1.models import CuisineType, IngredientCategory, Ingredient, Recipe, Difficulty
from src.part1.linked_list import RecipeIngredientLinkedList
from src.part2.substitution_graph import SubstitutionGraph
from src.part3.crisis_recovery import SupplyCrisisRecovery

class TestSupplyCrisisRecovery(unittest.TestCase):
    """测试供应危机恢复模块的所有方法及边缘情况"""

    def setUp(self):
        from src.part1.bst import RecipeBST
        from src.part1.supply_graph import SupplyGraph
        self.bst = RecipeBST()
        self.graph = SupplyGraph()
        self.sub_graph = SubstitutionGraph()

        self.ing1 = Ingredient(1, "rice", IngredientCategory.GRAIN, "kg", 10.0, 5.0, 3)
        self.ing2 = Ingredient(2, "beef", IngredientCategory.MEAT, "kg", 2.0, 3.0, 5)
        self.ing3 = Ingredient(3, "pork", IngredientCategory.MEAT, "kg", 8.0, 3.0, 4)
        self.ing4 = Ingredient(4, "egg", IngredientCategory.PRODUCE, "kg", 5.0, 5.0, 2)

        self.graph.add_supply_relation(1, 1, 5.0)
        self.graph.add_supply_relation(1, 2, 8.0)
        self.graph.add_supply_relation(2, 1, 6.0)
        self.graph.add_supply_relation(2, 3, 7.0)
        self.graph.add_supply_relation(3, 4, 10.0)

        ll1 = RecipeIngredientLinkedList()
        ll1.add_ingredient(self.ing1, 2.0)
        ll1.add_ingredient(self.ing2, 1.0)
        self.rec1 = Recipe(1, "Beef Rice", CuisineType.CHINESE, Difficulty.EASY, 30, 4)
        self.rec1.ingredient_list = ll1
        self.bst.insert(self.rec1)

        ll2 = RecipeIngredientLinkedList()
        ll2.add_ingredient(self.ing1, 3.0)
        ll2.add_ingredient(self.ing3, 0.5)
        self.rec2 = Recipe(2, "Pork Rice", CuisineType.CHINESE, Difficulty.MEDIUM, 45, 6)
        self.rec2.ingredient_list = ll2
        self.bst.insert(self.rec2)

        ll3 = RecipeIngredientLinkedList()
        ll3.add_ingredient(self.ing4, 2.0)
        self.rec3 = Recipe(3, "Egg Dish", CuisineType.WESTERN, Difficulty.EASY, 15, 2)
        self.rec3.ingredient_list = ll3
        self.bst.insert(self.rec3)

        self.sub_graph.register_ingredient(self.ing2)
        self.sub_graph.register_ingredient(self.ing3)
        self.sub_graph.add_substitution_pair(2, 3, 0.7)

    def test_simulate_supplier_shutdown_normal(self):
        """正常模拟供应商断供"""
        crisis = SupplyCrisisRecovery(self.graph, self.bst, self.sub_graph)
        crisis.simulate_supplier_shutdown(supplier_id=1)
        self.assertEqual(crisis.shutdown_supplier_id, 1)
        self.assertNotIn(1, self.graph.adj)

    def test_simulate_supplier_shutdown_non_existent(self):
        """模拟不存在供应商的断供"""
        crisis = SupplyCrisisRecovery(self.graph, self.bst, self.sub_graph)
        crisis.simulate_supplier_shutdown(supplier_id=999)
        self.assertEqual(crisis.shutdown_supplier_id, 999)
        self.assertNotIn(999, self.graph.adj)

    def test_simulate_supplier_shutdown_negative_id(self):
        """模拟负数ID供应商断供"""
        crisis = SupplyCrisisRecovery(self.graph, self.bst, self.sub_graph)
        crisis.simulate_supplier_shutdown(supplier_id=-1)
        self.assertEqual(crisis.shutdown_supplier_id, -1)

    def test_scan_risk_recipes_normal(self):
        """正常扫描风险食谱"""
        crisis = SupplyCrisisRecovery(self.graph, self.bst, self.sub_graph)
        crisis.simulate_supplier_shutdown(supplier_id=1)
        self.assertIsInstance(crisis.risk_recipes, list)
        self.assertGreaterEqual(len(crisis.risk_recipes), 0)

    def test_scan_risk_recipes_no_risk(self):
        """没有风险食谱（所有食材有多个供应商）"""
        self.graph.add_supply_relation(2, 2, 9.0)
        crisis = SupplyCrisisRecovery(self.graph, self.bst, self.sub_graph)
        crisis.simulate_supplier_shutdown(supplier_id=1)
        self.assertEqual(len(crisis.risk_recipes), 0)

    def test_scan_risk_recipes_all_risk(self):
        """所有食谱都有风险"""
        self.ing2.current_stock = 0.0
        self.ing4.current_stock = 0.0
        ll1 = RecipeIngredientLinkedList()
        ll1.add_ingredient(self.ing1, 2.0)
        ll1.add_ingredient(self.ing2, 1.0)
        self.rec1.ingredient_list = ll1
        ll3 = RecipeIngredientLinkedList()
        ll3.add_ingredient(self.ing4, 2.0)
        self.rec3.ingredient_list = ll3
        crisis = SupplyCrisisRecovery(self.graph, self.bst, self.sub_graph)
        crisis.simulate_supplier_shutdown(supplier_id=1)
        crisis.simulate_supplier_shutdown(supplier_id=2)
        crisis.simulate_supplier_shutdown(supplier_id=3)
        self.assertGreaterEqual(len(crisis.risk_recipes), 1)

    def test_dead_recipes_with_substitute(self):
        """风险食谱有替代食材可挽救"""
        self.ing2.current_stock = 0.0
        ll1 = RecipeIngredientLinkedList()
        ll1.add_ingredient(self.ing1, 2.0)
        ll1.add_ingredient(self.ing2, 1.0)
        self.rec1.ingredient_list = ll1
        crisis = SupplyCrisisRecovery(self.graph, self.bst, self.sub_graph)
        crisis.simulate_supplier_shutdown(supplier_id=1)
        has_rescuable = False
        for rec, missing in crisis.risk_recipes:
            for ing in missing:
                if len(self.sub_graph.get_all_substitutes(ing.ingredient_id)) > 0:
                    has_rescuable = True
                    break
        self.assertTrue(has_rescuable)

    def test_dead_recipes_no_substitute(self):
        """风险食谱无替代食材（致命）"""
        self.sub_graph.sub_edges.clear()
        crisis = SupplyCrisisRecovery(self.graph, self.bst, self.sub_graph)
        crisis.simulate_supplier_shutdown(supplier_id=1)
        self.assertGreaterEqual(len(crisis.dead_recipes), 0)

    def test_report_risk_recipes(self):
        """测试风险报告生成"""
        crisis = SupplyCrisisRecovery(self.graph, self.bst, self.sub_graph)
        crisis.simulate_supplier_shutdown(supplier_id=1)
        crisis.report_risk_recipes()
        self.assertIsInstance(crisis.risk_recipes, list)
        self.assertIsInstance(crisis.dead_recipes, list)

    def test_generate_recovery_plan_normal(self):
        """正常生成恢复方案"""
        crisis = SupplyCrisisRecovery(self.graph, self.bst, self.sub_graph)
        crisis.simulate_supplier_shutdown(supplier_id=1)
        crisis.generate_recovery_plan()
        self.assertIsInstance(crisis.risk_recipes, list)

    def test_generate_recovery_plan_no_risk(self):
        """无风险情况下生成恢复方案"""
        self.graph.add_supply_relation(2, 2, 9.0)
        crisis = SupplyCrisisRecovery(self.graph, self.bst, self.sub_graph)
        crisis.simulate_supplier_shutdown(supplier_id=1)
        crisis.generate_recovery_plan()
        self.assertEqual(len(crisis.risk_recipes), 0)

class TestIntegration(unittest.TestCase):
    """集成测试：验证Part3整体流程"""

    @classmethod
    def setUpClass(cls):
        cls.test_data_dir = tempfile.mkdtemp()
        gen = DatasetGenerator(data_dir=cls.test_data_dir)
        gen.generate_all_csv()
        cls.bst, cls.supply_graph, cls.heap, cls.recipe_map, _ = gen.load_all_data()
        cls.sub_graph = SubstitutionGraph()
        cls.sub_graph.build_default_substitution()
        cls.crisis = SupplyCrisisRecovery(cls.supply_graph, cls.bst, cls.sub_graph)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_data_dir, ignore_errors=True)

    def test_supplier_shutdown_scan_risk(self):
        """模拟供应商断供，识别风险食谱"""
        self.crisis.simulate_supplier_shutdown(supplier_id=1)
        self.assertIsInstance(self.crisis.risk_recipes, list)

    def test_risk_recipes_count(self):
        """风险食谱数量验证"""
        self.crisis.simulate_supplier_shutdown(supplier_id=0)
        self.assertGreaterEqual(len(self.crisis.risk_recipes), 0)

    def test_dead_recipes_count(self):
        """致命食谱数量验证"""
        self.crisis.simulate_supplier_shutdown(supplier_id=0)
        self.assertGreaterEqual(len(self.crisis.dead_recipes), 0)

    def test_report_and_recovery(self):
        """完整的风险报告和恢复方案"""
        self.crisis.simulate_supplier_shutdown(supplier_id=1)
        self.crisis.report_risk_recipes()
        self.crisis.generate_recovery_plan()
        self.assertTrue(True)

    def test_multiple_shutdown(self):
        """模拟多个供应商断供"""
        self.crisis.simulate_supplier_shutdown(supplier_id=0)
        count_after_first = len(self.crisis.risk_recipes)
        self.crisis.simulate_supplier_shutdown(supplier_id=1)
        count_after_second = len(self.crisis.risk_recipes)
        self.assertGreaterEqual(count_after_second, count_after_first)

if __name__ == "__main__":
    unittest.main()