import os
import unittest
from src.part1.dataset_generator import DatasetGenerator
from src.part1.models import CuisineType

def run_part1():
    """
    项目 Part1 完整执行入口
    功能：生成数据集 → 加载数据 → 构建四大数据结构 → 功能演示逻辑 → 单元测试
    """
    os.makedirs("data", exist_ok=True)
    generator = DatasetGenerator()

    # 生成符合所有约束的 CSV 数据集
    generator.generate_all_csv()

    # 加载数据，构建 BST、链表、供应图、采购堆
    bst, supply_graph, procurement_heap, recipe_map = generator.load_all_data()

    # BST 核心功能逻辑
    target_recipe = "Fried Rice"
    found_recipe = bst.search(target_recipe)
    chinese_recipes = bst.get_recipes_by_cuisine(CuisineType.CHINESE)
    range_recipes = bst.range_search("A", "F")
    feasible_recipes = bst.get_all_feasible_recipes()

    # 供应链图功能逻辑
    test_ing_id = 0
    suppliers = supply_graph.get_suppliers_for_ingredient(test_ing_id)
    cheap_sup = supply_graph.get_cheapest_supplier(test_ing_id)

    # 采购堆功能逻辑
    top5 = procurement_heap.get_top_k(5)

    # 运行 Part1 单元测试
    suite = unittest.TestLoader().discover("tests", pattern="test_part1.py")
    result = unittest.TextTestRunner(verbosity=0).run(suite)
    return bst, supply_graph, procurement_heap, recipe_map

if __name__ == "__main__":
    run_part1()