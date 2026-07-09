import os
import warnings
import logging
logging.getLogger('matplotlib.mathtext').setLevel(logging.ERROR)
warnings.filterwarnings('ignore', message="Font '.*' does not have a glyph for")
from src.part1.dataset_generator import DatasetGenerator
from src.part1.bst import RecipeBST
from src.part1.max_heap import UrgencyMaxHeap
from src.part2.substitution_graph import SubstitutionGraph
from src.part2.supplier_optimizer import SupplierOptimizer
from src.part2.menu_planner import WeeklyMenuPlanner
from src.part2.benchmark import BenchmarkTester
from src.part2.gui_app import run_gui
from src.part3.crisis_recovery import SupplyCrisisRecovery
import unittest

def run_part1():
    """Execute Part1: Data Model, Four Data Structures, CSV Generation, Unit Tests"""
    print("=" * 80)
    print("===== Part 1 - Basic Data Structure Toolkit (基础数据结构工具箱) =====")
    print("=" * 80)
    
    print("\n[1. Loading Data (加载数据)]")
    generator = DatasetGenerator()
    generator.generate_all_csv()
    bst, supply_graph, heap, recipe_map, supplier_map = generator.load_all_data()
    print("Data loaded successfully")
    
    print("\n[2. Data Statistics (数据统计)]")
    all_recipes = bst.in_order()
    print(f"Total recipes loaded in BST: {len(all_recipes)}")
    print(f"Ingredients in procurement heap: {heap.size()}")
    print(f"Suppliers in supply graph: {len(supplier_map)}")
    print(f"Total ingredients: {len(generator.ingredients)}")
    
    print("\n[3. Function Verification (功能验证)]")
    print("-" * 60)
    
    print("\n  [Recipe Search Test (食谱搜索测试)]")
    sample_recipe = list(recipe_map.values())[0]
    found = bst.search(sample_recipe.name)
    print(f"   Search '{sample_recipe.name}' -> {'Found' if found else 'Not Found'}")
    
    print("\n  [Cuisine Filter Test (菜系筛选测试)]")
    chinese_recipes = bst.get_recipes_by_cuisine("CHINESE")
    print(f"   Chinese recipes count: {len(chinese_recipes)}")
    
    print("\n  [Alphabet Range Search Test (字母范围搜索测试)]")
    af_recipes = bst.range_search("A", "F")
    print(f"   Recipes from A-F: {len(af_recipes)}")
    
    print("\n  [Procurement Heap Top5 Test (采购堆Top5测试)]")
    top5 = heap.get_top_k(5)
    for score, ing in top5:
        print(f"   {ing.name} - Urgency:{score:.2f}")
    
    print("\n  [Supply Network Test (供应网络测试)]")
    sample_ing = generator.ingredients[0]
    suppliers = supply_graph.get_suppliers_for_ingredient(sample_ing.ingredient_id)
    print(f"   Suppliers for '{sample_ing.name}': {len(suppliers)}")
    
    print("\n[4. Run Part1 Unit Tests (执行Part1单元测试)]")
    print("-" * 60)
    suite = unittest.TestLoader().discover("tests", pattern="test_part1.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"\n  Part1 Test Result: {result.testsRun} tests, {passed} passed")
    
    return bst, supply_graph, heap, recipe_map, supplier_map, generator

def run_part2(bst, supply_graph, heap, recipe_map, supplier_map, generator):
    """Execute Part2: Substitution Algorithm, Supplier Optimization, Menu Planning, Performance Test, GUI"""
    print("\n" + "=" * 80)
    print("===== Part 2 - Advanced Graph and Optimization Algorithms (高级图与优化算法) =====")
    print("=" * 80)
    
    all_recipes = bst.in_order()
    
    print("\n[1. Build Ingredient Substitution Graph (构建食材替换图)]")
    sub_graph = SubstitutionGraph()
    sub_graph.build_default_substitution()
    for ing in generator.ingredients:
        sub_graph.register_ingredient(ing)
    print(f"Ingredient substitution network built, registered {len(generator.ingredients)} ingredients")
    
    print("\n[2. Function Verification (功能验证)]")
    print("-" * 60)
    
    print("\n  [Ingredient Substitution Test (食材替换测试)]")
    subs = sub_graph.get_all_substitutes(4)
    print(f"   Substitutes for ingredient ID=4: {len(subs)}")
    
    print("\n  [Optimal Supplier Test (最优供应商测试)]")
    optimizer = SupplierOptimizer(supply_graph)
    for sup in supplier_map.values():
        optimizer.add_supplier(sup)
    sample_recipe = list(recipe_map.values())[0]
    best_suppliers, total_cost = optimizer.get_min_cost_supplier_set(sample_recipe, reliability_threshold=0.6)
    print(f"   Optimal supplier cost for '{sample_recipe.name}': {total_cost:.2f}")
    
    print("\n  [Weekly Menu Feasibility Planning (周菜单可行性规划)]")
    menu_planner = WeeklyMenuPlanner(bst, heap, supply_graph)
    test_menu = list(recipe_map.values())[:3]
    shortage, procure_plan = menu_planner.analyze_menu(test_menu)
    print(f"   Ingredients in shortage: {len(shortage)}")
    
    print("\n[3. Menu Display (菜单展示)]")
    print("-" * 60)
    print(f"\n  Total recipes in system: {len(all_recipes)}")
    for i, recipe in enumerate(all_recipes[:10], 1):
        is_feasible, _ = recipe.ingredient_list.check_recipe_feasible()
        status = "[right]" if is_feasible else "[error]"
        print(f"   {i}. {status} {recipe.name} ({recipe.cuisine_type.name}, {recipe.difficulty.name})")
    if len(all_recipes) > 10:
        print(f"   ... and {len(all_recipes) - 10} more recipes")
    
    print("\n[4. Performance Benchmark (性能基准测试)]")
    print("-" * 60)
    tester = BenchmarkTester()
    tester.run_benchmark()
    print("Performance benchmark chart saved to ./reports/")
    
    print("\n[5. Run Part2 Unit Tests (执行Part2单元测试)]")
    print("-" * 60)
    suite = unittest.TestLoader().discover("tests", pattern="test_part2.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"\n  Part2 Test Result: {result.testsRun} tests, {passed} passed")
    
    print("\n[6. Launch Visualization GUI (启动可视化GUI)]")
    print("-" * 60)
    print("  GUI Features:")
    print("  • Recipe Search - Search recipe by name, view details")
    print("  • Cuisine Filter - Filter recipes by cuisine type")
    print("  • Alphabet Range - Search recipes by alphabet range")
    print("  • Ingredient Substitution - Query ingredient substitutes")
    print("  • Supply Network - Query ingredient suppliers")
    print("  • Test Results - Run all tests with detailed report")
    print("\n  Starting GUI...")
    
    run_gui(bst, supply_graph, heap, sub_graph, supplier_map)
    return sub_graph, optimizer, menu_planner

def run_part3(supply_graph, bst, recipe_map, sub_graph):
    """Execute Part3: Supplier Shutdown Crisis Recovery Plan"""
    print("\n" + "=" * 80)
    print("===== Part 3 - Supply Chain Crisis Recovery Challenge (供应链危机恢复挑战) =====")
    print("=" * 80)
    
    print("\n[1. Simulate Supplier Shutdown (模拟供应商断供)]")
    crisis = SupplyCrisisRecovery(supply_graph, bst, sub_graph)
    crisis.simulate_supplier_shutdown(supplier_id=0)
    
    print("\n[2. Risk Assessment (风险评估)]")
    crisis.report_risk_recipes()
    
    print("\n[3. Generate Recovery Plan (生成恢复方案)]")
    crisis.generate_recovery_plan()
    
    print("\n[4. Run Part3 Unit Tests (执行Part3单元测试)]")
    print("-" * 60)
    suite = unittest.TestLoader().discover("tests", pattern="test_part3.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"\n  Part3 Test Result: {result.testsRun} tests, {passed} passed")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    print("=" * 80)
    print("=== Supply Chain Optimization System - One-Click Run Mode (供应链优化系统 - 一键运行模式) ===")
    print("=" * 80)
    print("\nThe system will automatically run all modules in sequence:")
    print("  1. Part1 - Basic Data Structure + Dataset")
    print("  2. Part2 - Advanced Algorithm + Visualization GUI")
    print("  3. Part3 - Crisis Recovery Simulation")
    print("\n" + "=" * 80 + "\n")
    
    try:
        bst, sg, heap, rmap, sup_map, generator = run_part1()
        sub_g, opt, planner = run_part2(bst, sg, heap, rmap, sup_map, generator)
        run_part3(sg, bst, rmap, sub_g)
        
        print("\n" + "=" * 80)
        print("All modules completed successfully!")
        print("=" * 80)
    except Exception as e:
        print(f"\nError occurred during execution: {e}")
        import traceback
        traceback.print_exc()
