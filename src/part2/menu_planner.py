from src.part1.bst import RecipeBST
from src.part1.max_heap import UrgencyMaxHeap
from src.part1.supply_graph import SupplyGraph
from typing import List, Dict, Optional
import random

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
        for rec in menu_recipes:
            feasible, missing = rec.ingredient_list.check_recipe_feasible()
            for ing in missing:
                shortage_ings.add(ing)
        procure_plan = self.heap.get_top_k(len(shortage_ings))
        return list(shortage_ings), procure_plan

    def generate_procurement_plan(self):
        """生成采购计划，返回按紧急度排序的食材列表"""
        all_recipes = self.bst.in_order()
        shortage_ings, procure_plan = self.analyze_menu(all_recipes)
        return procure_plan

    def get_all_recipes(self) -> List:
        """获取BST中所有食谱"""
        return self.bst.in_order()

    def get_feasible_recipes(self) -> List:
        """获取所有库存充足的可行食谱"""
        all_recipes = self.bst.in_order()
        feasible = []
        for rec in all_recipes:
            is_feasible, _ = rec.ingredient_list.check_recipe_feasible()
            if is_feasible:
                feasible.append(rec)
        return feasible

    def get_recipe_feasibility(self, recipe) -> Dict:
        """获取单个食谱的可行性状态"""
        feasible, missing = recipe.ingredient_list.check_recipe_feasible()
        return {
            'recipe': recipe,
            'feasible': feasible,
            'missing': missing
        }

    def generate_weekly_menu(self, week_offset: int = 0) -> List[Dict]:
        """
        生成每周菜单规划：
        根据当前库存状态，为周一到周日分配食谱
        优先选择库存充足的食谱，若不足则标注缺口食材
        
        Args:
            week_offset: 周偏移量，0=本周，1=下周
        """
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        all_recipes = self.bst.in_order()
        
        random.seed(42 + week_offset)
        shuffled_recipes = all_recipes.copy()
        random.shuffle(shuffled_recipes)
        
        feasible_recipes = []
        infeasible_recipes = []
        
        for rec in shuffled_recipes:
            if rec.ingredient_list is None:
                continue
            is_feasible, missing = rec.ingredient_list.check_recipe_feasible()
            if is_feasible:
                feasible_recipes.append((rec, []))
            else:
                infeasible_recipes.append((rec, missing))
        
        weekly_menu = []
        available_recipes = feasible_recipes + infeasible_recipes
        
        for i, day in enumerate(days):
            if available_recipes:
                rec, missing = available_recipes.pop(0)
                is_feasible = len(missing) == 0
                weekly_menu.append({
                    'day': day,
                    'day_index': i,
                    'week_offset': week_offset,
                    'recipe': rec,
                    'feasible': is_feasible,
                    'missing': missing
                })
            else:
                weekly_menu.append({
                    'day': day,
                    'day_index': i,
                    'week_offset': week_offset,
                    'recipe': None,
                    'feasible': None,
                    'missing': []
                })
        
        return weekly_menu

    def generate_next_week_menu(self) -> List[Dict]:
        """
        推算下周菜单：
        基于本周菜单消耗后的库存状态推算下周可用食谱
        """
        return self.generate_weekly_menu(week_offset=1)