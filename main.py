import os
from src.part1.dataset_generator import DatasetGenerator
from src.part1.bst import RecipeBST
from src.part1.max_heap import UrgencyMaxHeap  # 修复：UrgencyHeap → UrgencyMaxHeap
from src.part2.substitution_graph import SubstitutionGraph
from src.part2.supplier_optimizer import SupplierOptimizer
from src.part2.menu_planner import WeeklyMenuPlanner
from src.part2.benchmark import BenchmarkTester
from src.part2.gui_app import run_gui
from src.part3.crisis_recovery import SupplyCrisisRecovery
import unittest

def run_part1():
    """执行Part1：数据模型、四大数据结构、CSV生成、单元测试"""
    print("===== Running Part 1 - Core Data Structure Toolbox =====")
    # 1. 生成CSV数据集
    generator = DatasetGenerator()
    generator.generate_all_csv()
    print("✅ CSV数据集生成完成，存放于 ./data/")

    # 2. 加载数据构建全部结构
    bst, supply_graph, heap, recipe_map = generator.load_all_data()
    print(f"✅ BST加载食谱总数：{len(bst.in_order())}")
    print(f"✅ 采购堆当前待补货食材：{heap.size()}")

    # 3. 执行Part1单元测试
    print("\n----- Execute Part1 Unit Tests -----")
    suite = unittest.TestLoader().discover("tests", pattern="test_part1.py")
    unittest.TextTestRunner().run(suite)
    return bst, supply_graph, heap, recipe_map

def run_part2(bst, supply_graph, heap, recipe_map):
    """执行Part2：替换算法、供应商优化、菜单规划、性能测试、GUI"""
    print("\n===== Running Part 2 - Advanced Graph & Optimization Algorithms =====")
    # 1. 构建食材替换图
    sub_graph = SubstitutionGraph()
    sub_graph.build_default_substitution()
    print("✅ 食材替换网络构建完成")

    # 2. 最优供应商测试
    optimizer = SupplierOptimizer(supply_graph)
    sample_recipe = list(recipe_map.values())[0]
    best_suppliers, total_cost = optimizer.get_min_cost_supplier_set(sample_recipe, reliability_threshold=0.6)
    print(f"✅ 样例食谱最优供应商总成本：{total_cost:.2f}")

    # 3. 周菜单可行性规划
    menu_planner = WeeklyMenuPlanner(bst, heap, supply_graph)
    test_menu = list(recipe_map.values())[:3]
    shortage, procure_plan = menu_planner.analyze_menu(test_menu)
    print(f"✅ 周菜单库存缺口食材数量：{len(shortage)}")

    # 4. 性能基准测试并绘图
    tester = BenchmarkTester()
    tester.run_benchmark()
    print("✅ 性能基准图表已保存至 ./reports/")

    # 5. 启动GUI（可选）
    choice = input("\n是否启动可视化GUI？(y/n): ")
    if choice.lower() == "y":
        run_gui(bst, supply_graph, heap, sub_graph)
    return sub_graph, optimizer, menu_planner

def run_part3(supply_graph, bst, recipe_map, sub_graph):
    """执行Part3：供应商断供危机恢复方案"""
    print("\n===== Running Part 3 - Supply Chain Crisis Recovery Challenge =====")
    crisis = SupplyCrisisRecovery(supply_graph, bst, sub_graph)
    # 模拟移除编号0的核心供应商
    crisis.simulate_supplier_shutdown(supplier_id=0)
    crisis.report_risk_recipes()
    crisis.generate_recovery_plan()
    # 执行Part3单元测试
    print("\n----- Execute Part3 Unit Tests -----")
    suite = unittest.TestLoader().discover("tests", pattern="test_part3.py")
    unittest.TextTestRunner().run(suite)

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    print("=== Recipe & Ingredient Supply Chain Optimizer ===")
    print("请选择运行阶段：")
    print("1 - 仅运行 Part1 (基础数据结构+数据集)")
    print("2 - 运行 Part1 + Part2 (全部基础+高级算法GUI)")
    print("3 - 完整运行 Part1 + Part2 + Part3 (含断供危机模拟)")
    opt = input("输入数字(1/2/3): ")

    if opt == "1":
        run_part1()
    elif opt == "2":
        bst, sg, heap, rmap = run_part1()
        run_part2(bst, sg, heap, rmap)
    elif opt == "3":
        bst, sg, heap, rmap = run_part1()
        sub_g, opt, planner = run_part2(bst, sg, heap, rmap)
        run_part3(sg, bst, rmap, sub_g)
    else:
        print("输入无效，退出程序")