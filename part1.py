import tempfile
import shutil
import os

from src.part1.dataset_generator import DatasetGenerator
from src.part1.models import Ingredient, Recipe, CuisineType, Difficulty, IngredientCategory
from src.part1.linked_list import RecipeIngredientLinkedList
from src.part1.bst import RecipeBST
from src.part1.max_heap import UrgencyMaxHeap
from src.part1.supply_graph import SupplyGraph


def print_recipe_details(bst: RecipeBST, supply_graph: SupplyGraph):
    all_recipes = bst.in_order()
    
    print("=" * 80)
    print("Supply Chain Optimization System - Recipe Details (食谱详情)")
    print("=" * 80)
    print(f"Total Recipes (食谱总数): {len(all_recipes)}")
    print("-" * 80)
    
    for idx, recipe in enumerate(all_recipes, 1):
        print(f"\n[{idx}] Recipe: {recipe.name}")
        print(f"   ID: {recipe.recipe_id}")
        print(f"   Cuisine (菜系): {recipe.cuisine_type.value}")
        print(f"   Difficulty (难度): {recipe.difficulty.value}")
        print(f"   Prep Time (准备时间): {recipe.prep_time_minutes} minutes")
        print(f"   Servings (人数): {recipe.servings}")
        
        if recipe.ingredient_list:
            print(f"   Ingredients (食材):")
            ingredients = recipe.ingredient_list.get_all_ingredients()
            for ing, qty in ingredients:
                suppliers = supply_graph.get_suppliers_for_ingredient(ing.ingredient_id)
                cheapest_sup = supply_graph.get_cheapest_supplier(ing.ingredient_id)
                cost_info = f"| Cheapest: {cheapest_sup[0]} @ {cheapest_sup[1]} per {ing.unit}" if cheapest_sup else ""
                print(f"     - {ing.name} ({ing.category.value}): {qty}{ing.unit} (Stock: {ing.current_stock}/{ing.minimum_stock}){cost_info}")
        else:
            print("   Ingredients (食材): None")
    
    print("\n" + "=" * 80)


def main():
    temp_dir = tempfile.mkdtemp()
    try:
        gen = DatasetGenerator(data_dir=temp_dir)
        gen.generate_all_csv()
        bst, supply_graph, heap, recipe_map, supplier_map = gen.load_all_data()
        
        print_recipe_details(bst, supply_graph)
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()