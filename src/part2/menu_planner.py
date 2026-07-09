from src.part1.bst import RecipeBST
from src.part1.max_heap import UrgencyMaxHeap
from src.part1.supply_graph import SupplyGraph

class WeeklyMenuPlanner:
    def __init__(self, bst: RecipeBST, heap: UrgencyMaxHeap, supply_graph: SupplyGraph):
        self.bst = bst
        self.heap = heap
        self.graph = supply_graph

    def analyze_menu(self, menu_recipes: list):
        """
        分析整周菜单：
        1. 汇总所有缺口食材
        2. 生成按紧急度排序的采购计划
        返回 (短缺食材集合, 优先级采购列表)
        """
        shortage_ings = set()
        # 遍历所有菜品，收集缺口
        for rec in menu_recipes:
            feasible, missing = rec.ingredient_list.check_recipe_feasible()
            for ing in missing:
                shortage_ings.add(ing)
        # 提取topK紧急食材作为采购计划
        procure_plan = self.heap.get_top_k(len(shortage_ings))
        return list(shortage_ings), procure_plan

    def generate_procurement_plan(self):
        """生成采购计划，返回按紧急度排序的食材列表"""
        all_recipes = self.bst.in_order()
        shortage_ings, procure_plan = self.analyze_menu(all_recipes)
        return procure_plan