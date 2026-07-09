import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
from src.part1.bst import RecipeBST
from src.part1.supply_graph import SupplyGraph
from src.part1.max_heap import UrgencyMaxHeap
from src.part1.models import Supplier
from src.part2.substitution_graph import SubstitutionGraph
from src.part3.crisis_recovery import SupplyCrisisRecovery
import unittest
import io
import sys
import os
import numpy as np

class TestResultCapture(unittest.TextTestRunner):
    def __init__(self, stream=None, descriptions=True, verbosity=2):
        self.output = []
        super().__init__(stream=io.StringIO(), descriptions=descriptions, verbosity=verbosity)

    def run(self, test):
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        try:
            result = super().run(test)
            self.output = sys.stdout.getvalue()
            return result, self.output
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

def run_single_function_test(func_name, test_func, description):
    try:
        test_func()
        return True, f"[right] {func_name} - {description}"
    except Exception as e:
        return False, f"[error] {func_name} - {description}\n   Error: {str(e)[:100]}"

def run_gui(bst: RecipeBST, supply_graph: SupplyGraph, heap: UrgencyMaxHeap, sub_graph: SubstitutionGraph):
    root = tk.Tk()
    root.title("Supply Chain Optimization System (供应链优化系统)")
    root.geometry("1400x900")

    notebook = ttk.Notebook(root)
    
    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    tab3 = ttk.Frame(notebook)
    tab4 = ttk.Frame(notebook)
    tab5 = ttk.Frame(notebook)
    tab6 = ttk.Frame(notebook)
    tab7 = ttk.Frame(notebook)
    tab8 = ttk.Frame(notebook)
    tab9 = ttk.Frame(notebook)
    tab10 = ttk.Frame(notebook)
    
    notebook.add(tab1, text="Recipe Search (食谱搜索)")
    notebook.add(tab2, text="Cuisine Filter (菜系筛选)")
    notebook.add(tab3, text="Alphabet Range (字母范围搜索)")
    notebook.add(tab4, text="Ingredient Substitution (食材替换)")
    notebook.add(tab5, text="Supply Network (供应网络)")
    notebook.add(tab6, text="Performance Chart (性能图表)")
    notebook.add(tab7, text="Test Results (测试结果)")
    notebook.add(tab8, text="Data Management (数据管理)")
    notebook.add(tab9, text="Structure Visualization (结构可视化)")
    notebook.add(tab10, text="Crisis Recovery (危机恢复)")
    notebook.pack(fill=tk.BOTH, expand=True)

    all_recipes = bst.in_order()

    def show_recipe_detail(recipe):
        if recipe is None:
            return
        ing_list = recipe.ingredient_list.get_all_ingredients()
        text = f"Recipe: {recipe.name}\n"
        text += f"Cuisine: {recipe.cuisine_type.value}\n"
        text += f"Difficulty: {recipe.difficulty.value}\n"
        text += f"Prep Time: {recipe.prep_time_minutes} mins\n"
        text += f"Serving: {recipe.servings} people\n"
        text += "Ingredients:\n"
        for ing, qty in ing_list:
            text += f"- {ing.name} ({ing.category.value}) need {qty}{ing.unit} stock:{ing.current_stock}/{ing.minimum_stock}\n"
        messagebox.showinfo("Recipe Detail (食谱详情)", text)

    # Tab1: Recipe Search (食谱搜索)
    ttk.Label(tab1, text="Search Recipe Name:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    search_entry = ttk.Entry(tab1, width=40)
    search_entry.grid(row=0, column=1, padx=10, pady=10)
    
    search_result = tk.Listbox(tab1, width=80, height=20)
    search_result.grid(row=1, column=0, columnspan=3, padx=10, pady=5)
    
    def do_search():
        search_result.delete(0, tk.END)
        name = search_entry.get().strip()
        if not name:
            for r in all_recipes[:10]:
                search_result.insert(tk.END, f"{r.name} | {r.cuisine_type.value} | {r.difficulty.value}")
            search_result.insert(tk.END, f"\nShowing top 10 recipes, total {len(all_recipes)}")
            return
        found = bst.search(name)
        if found:
            search_result.insert(tk.END, f"[right] Found: {found.name}")
            search_result.insert(tk.END, f"   Cuisine: {found.cuisine_type.value}")
            search_result.insert(tk.END, f"   Difficulty: {found.difficulty.value}")
            search_result.insert(tk.END, f"   Prep Time: {found.prep_time_minutes} mins")
        else:
            search_result.insert(tk.END, f"[error] Not found: '{name}'")
    
    ttk.Button(tab1, text="Search", command=do_search).grid(row=0, column=2, padx=10, pady=10)
    
    def view_selected_detail():
        idx = search_result.curselection()
        if not idx:
            messagebox.showwarning("Warning", "Please select a recipe first")
            return
        selected_text = search_result.get(idx[0])
        if "[right] Found:" in selected_text:
            recipe_name = selected_text.replace("[right] Found: ", "").strip()
        elif "Showing top" in selected_text or "[error]" in selected_text:
            messagebox.showwarning("Warning", "Please select a valid recipe")
            return
        else:
            recipe_name = selected_text.split("|")[0].strip()
        recipe = bst.search(recipe_name)
        show_recipe_detail(recipe)
    
    ttk.Button(tab1, text="View Detail", command=view_selected_detail).grid(row=2, column=0, padx=10, pady=10)
    
    search_result.insert(tk.END, "=== Showing top 10 recipes ===")
    for r in all_recipes[:10]:
        search_result.insert(tk.END, f"{r.name} | {r.cuisine_type.value} | {r.difficulty.value}")

    # Tab2: Cuisine Filter (菜系筛选)
    ttk.Label(tab2, text="Select Cuisine:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    cuisine_var = tk.StringVar()
    cuisine_combo = ttk.Combobox(tab2, textvariable=cuisine_var, width=20)
    cuisine_combo['values'] = ('CHINESE', 'WESTERN', 'JAPANESE', 'ALL')
    cuisine_combo.current(3)
    cuisine_combo.grid(row=0, column=1, padx=10, pady=10)
    
    cuisine_result = tk.Listbox(tab2, width=80, height=20)
    cuisine_result.grid(row=1, column=0, columnspan=3, padx=10, pady=5)
    
    def filter_by_cuisine():
        cuisine_result.delete(0, tk.END)
        cuisine = cuisine_var.get()
        if cuisine == 'ALL':
            recipes = all_recipes
        else:
            recipes = bst.get_recipes_by_cuisine(cuisine)
        if recipes:
            for idx, r in enumerate(recipes, 1):
                cuisine_result.insert(tk.END, f"{idx}. {r.name} | {r.cuisine_type.value} | {r.difficulty.value}")
            cuisine_result.insert(tk.END, f"\nFound {len(recipes)} recipes")
        else:
            cuisine_result.insert(tk.END, "[error] No recipes found for this cuisine")
    
    ttk.Button(tab2, text="Filter", command=filter_by_cuisine).grid(row=0, column=2, padx=10, pady=10)
    ttk.Button(tab2, text="View Detail", command=lambda: show_recipe_detail(bst.search(cuisine_result.get(cuisine_result.curselection()).split('.')[1].strip().split('|')[0].strip()) if cuisine_result.curselection() else None)).grid(row=2, column=0, padx=10, pady=10)
    
    filter_by_cuisine()

    # Tab3: Alphabet Range (字母范围搜索)
    ttk.Label(tab3, text="Start Letter:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    start_entry = ttk.Entry(tab3, width=10)
    start_entry.grid(row=0, column=1, padx=5, pady=10)
    start_entry.insert(0, "A")
    
    ttk.Label(tab3, text="End Letter:").grid(row=0, column=2, padx=10, pady=10, sticky="w")
    end_entry = ttk.Entry(tab3, width=10)
    end_entry.grid(row=0, column=3, padx=5, pady=10)
    end_entry.insert(0, "F")
    
    range_result = tk.Listbox(tab3, width=80, height=20)
    range_result.grid(row=1, column=0, columnspan=4, padx=10, pady=5)
    
    def search_by_range():
        range_result.delete(0, tk.END)
        start = start_entry.get().strip().upper()
        end = end_entry.get().strip().upper()
        if not start or not end:
            messagebox.showwarning("Warning", "Please enter start and end letters")
            return
        recipes = bst.range_search(start, end)
        if recipes:
            for idx, r in enumerate(recipes, 1):
                range_result.insert(tk.END, f"{idx}. {r.name} | {r.cuisine_type.value}")
            range_result.insert(tk.END, f"\nFound {len(recipes)} recipes")
        else:
            range_result.insert(tk.END, "[error] No recipes in this range")
    
    ttk.Button(tab3, text="Search", command=search_by_range).grid(row=0, column=4, padx=10, pady=10)
    
    search_by_range()

    # Tab4: Ingredient Substitution (食材替换)
    ttk.Label(tab4, text="Enter Ingredient ID to find substitutes:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    sub_entry = ttk.Entry(tab4, width=10)
    sub_entry.grid(row=0, column=1, padx=10, pady=10)
    
    sub_result = scrolledtext.ScrolledText(tab4, width=80, height=20)
    sub_result.grid(row=1, column=0, columnspan=3, padx=10, pady=5)
    
    def query_sub():
        sub_result.delete(1.0, tk.END)
        try:
            iid = int(sub_entry.get())
            subs = sub_graph.get_all_substitutes(iid)
            if subs:
                sub_result.insert(tk.END, "Substitute Ingredients (sorted by quality):\n")
                sub_result.insert(tk.END, "-" * 60 + "\n")
                for ing, score in subs:
                    sub_result.insert(tk.END, f"[right] {ing.name} ({ing.category.value}) - Match: {score:.2f}\n")
            else:
                sub_result.insert(tk.END, "[error] No substitutes found\n")
        except ValueError:
            sub_result.insert(tk.END, "[error] Please enter valid number ID\n")

    ttk.Button(tab4, text="Find Substitutes", command=query_sub).grid(row=0, column=2, padx=10, pady=10)

    sub_result.insert(tk.END, "=== Default Substitution Graph Info ===\n")
    sub_result.insert(tk.END, "-" * 60 + "\n")
    sub_result.insert(tk.END, f"Registered ingredients: {len(sub_graph.ingredient_map)}\n")
    sub_result.insert(tk.END, f"Substitution relationships: {len(sub_graph.sub_edges)}\n")
    sub_result.insert(tk.END, "\nExample: Enter ingredient ID 1-10 to find substitutes\n")

    # Tab5: Supply Network (供应网络)
    ttk.Label(tab5, text="Enter Ingredient ID to find suppliers:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    ing_entry = ttk.Entry(tab5, width=10)
    ing_entry.grid(row=0, column=1, padx=10, pady=10)
    
    supply_result = scrolledtext.ScrolledText(tab5, width=80, height=20)
    supply_result.grid(row=1, column=0, columnspan=3, padx=10, pady=5)
    
    def query_supplier():
        supply_result.delete(1.0, tk.END)
        try:
            iid = int(ing_entry.get())
            sids = supply_graph.get_suppliers_for_ingredient(iid)
            if sids:
                supply_result.insert(tk.END, "Supplier List:\n")
                supply_result.insert(tk.END, "-" * 60 + "\n")
                for sid in sids:
                    cost = supply_graph.get_unit_cost(sid, iid)
                    supply_result.insert(tk.END, f"[right] Supplier{sid} - Unit Price: {cost:.2f}\n")
            else:
                supply_result.insert(tk.END, "[error] No suppliers for this ingredient\n")
        except ValueError:
            supply_result.insert(tk.END, "[error] Please enter valid number ID\n")

    ttk.Button(tab5, text="Find Suppliers", command=query_supplier).grid(row=0, column=2, padx=10, pady=10)

    supply_result.insert(tk.END, "=== Default Supply Network Info ===\n")
    supply_result.insert(tk.END, "-" * 60 + "\n")
    supply_result.insert(tk.END, f"Suppliers count: {len(supply_graph.adj)}\n")
    total_relations = sum(len(v) for v in supply_graph.adj.values())
    supply_result.insert(tk.END, f"Supply relationships: {total_relations}\n")
    supply_result.insert(tk.END, f"Ingredient types: {len(supply_graph.ingredient_to_suppliers)}\n")
    supply_result.insert(tk.END, "\nExample: Enter ingredient ID 1-10 to find suppliers\n")

    # Tab6: Performance Chart (性能图表)
    chart_frame = ttk.Frame(tab6)
    chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    chart_label = ttk.Label(chart_frame, text="Performance Benchmark Chart")
    chart_label.pack(pady=5)
    
    control_frame = ttk.Frame(chart_frame)
    control_frame.pack(fill=tk.X, pady=3)
    
    ttk.Button(control_frame, text="Refresh", command=lambda: load_chart(1.0)).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Zoom In (+)", command=lambda: zoom_chart(1.2)).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Zoom Out (-)", command=lambda: zoom_chart(0.8)).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Reset", command=lambda: zoom_chart(1.0)).pack(side=tk.LEFT, padx=5)
    
    zoom_label = ttk.Label(control_frame, text="Zoom: 100%")
    zoom_label.pack(side=tk.RIGHT, padx=10)
    
    scroll_frame = ttk.Frame(chart_frame)
    scroll_frame.pack(fill=tk.BOTH, expand=True)
    
    v_scrollbar = ttk.Scrollbar(scroll_frame, orient=tk.VERTICAL)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    h_scrollbar = ttk.Scrollbar(scroll_frame, orient=tk.HORIZONTAL)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    canvas = tk.Canvas(scroll_frame, bg="white", width=800, height=500,
                       yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    v_scrollbar.config(command=canvas.yview)
    h_scrollbar.config(command=canvas.xview)
    
    chart_img = None
    current_scale = 1.0
    original_width = 800
    original_height = 500
    
    def load_chart(scale=1.0):
        global chart_img, current_scale, original_width, original_height
        chart_path = "./reports/benchmark_plot.png"
        if os.path.exists(chart_path):
            try:
                img = Image.open(chart_path)
                original_width, original_height = img.size
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                chart_img = ImageTk.PhotoImage(img)
                canvas.delete("all")
                canvas.create_image(0, 0, anchor=tk.NW, image=chart_img)
                canvas.config(scrollregion=(0, 0, new_width, new_height))
                current_scale = scale
                zoom_label.config(text=f"Zoom: {int(scale * 100)}%")
            except Exception as e:
                canvas.delete("all")
                canvas.create_text(400, 250, text=f"Failed to load image: {e}", font=("Arial", 12))
        else:
            canvas.delete("all")
            canvas.create_text(400, 200, text="benchmark_plot.png not found", font=("Arial", 14))
            canvas.create_text(400, 250, text="Please run performance test first", font=("Arial", 12))
            canvas.create_text(400, 300, text="Path: ./reports/benchmark_plot.png", font=("Arial", 10))
    
    def zoom_chart(factor):
        global current_scale
        new_scale = max(0.25, min(3.0, current_scale * factor))
        load_chart(new_scale)
    
    load_chart()

    # Tab7: Test Results (测试结果)
    test_result = scrolledtext.ScrolledText(tab7, width=100, height=30)
    test_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    progress_bar = ttk.Progressbar(tab7, mode='indeterminate')
    progress_bar.pack(fill=tk.X, padx=10, pady=5)
    
    def run_all_tests():
        test_result.delete(1.0, tk.END)
        progress_bar.start()
        
        test_result.insert(tk.END, "=" * 80 + "\n")
        test_result.insert(tk.END, "           Supply Chain Optimization System - Automated Test Report\n")
        test_result.insert(tk.END, "=" * 80 + "\n\n")
        
        all_passed = True
        total_tests = 0
        passed_tests = 0
        
        test_result.insert(tk.END, "=" * 80 + "\n")
        test_result.insert(tk.END, "[Part1 - Basic Data Structure (基础数据结构)]\n")
        test_result.insert(tk.END, "=" * 80 + "\n\n")
        
        test_result.insert(tk.END, "--- Linked List Operations (链表操作) ---\n")
        test_cases = []
        
        from src.part1.linked_list import RecipeIngredientLinkedList
        from src.part1.models import Ingredient, IngredientCategory
        ll = RecipeIngredientLinkedList()
        ing1 = Ingredient(1, "rice", IngredientCategory.GRAIN, "kg", 10.0, 5.0, 3)
        ing2 = Ingredient(2, "beef", IngredientCategory.MEAT, "kg", 5.0, 3.0, 5)
        ing3 = Ingredient(3, "egg", IngredientCategory.PRODUCE, "kg", 20.0, 10.0, 2)
        
        test_cases.append(("add_ingredient", lambda: ll.add_ingredient(ing1, 2.0), "Add ingredient"))
        test_cases.append(("get_all_ingredients", lambda: ll.get_all_ingredients(), "Get all ingredients"))
        test_cases.append(("size", lambda: ll.size, "Get list size"))
        test_cases.append(("update_quantity", lambda: ll.update_quantity(1, 3.0), "Update quantity"))
        test_cases.append(("remove_ingredient", lambda: ll.remove_ingredient(1), "Remove ingredient"))
        test_cases.append(("get_quantity", lambda: ll.get_quantity(1), "Get quantity (non-existent)"))
        test_cases.append(("get_all_empty", lambda: RecipeIngredientLinkedList().get_all_ingredients(), "Get empty list"))
        
        test_result.insert(tk.END, "\n--- Tail Pointer Tests (尾指针测试) ---\n")
        
        ll_tail = RecipeIngredientLinkedList()
        ing_t1 = Ingredient(101, "flour", IngredientCategory.GRAIN, "kg", 10.0, 5.0, 3)
        ing_t2 = Ingredient(102, "sugar", IngredientCategory.GRAIN, "kg", 5.0, 3.0, 2)
        ing_t3 = Ingredient(103, "milk", IngredientCategory.DAIRY, "L", 8.0, 4.0, 1)
        
        def test_tail_add():
            ll_tail.add_ingredient(ing_t1, 1.0)
            assert ll_tail.tail is not None, "Tail should not be None after add"
            assert ll_tail.tail.ingredient.ingredient_id == 101, "Tail should point to first element"
            ll_tail.add_ingredient(ing_t2, 0.5)
            assert ll_tail.tail.ingredient.ingredient_id == 102, "Tail should point to second element"
            ll_tail.add_ingredient(ing_t3, 2.0)
            assert ll_tail.tail.ingredient.ingredient_id == 103, "Tail should point to third element"
            return True
        
        def test_tail_single_node():
            ll_single = RecipeIngredientLinkedList()
            ll_single.add_ingredient(ing_t1, 1.0)
            assert ll_single.head is ll_single.tail, "Head and tail should be same for single node"
            return True
        
        def test_tail_remove_head():
            ll_tail.remove_ingredient(101)
            assert ll_tail.tail is not None, "Tail should not be None after removing head"
            assert ll_tail.tail.ingredient.ingredient_id == 103, "Tail should still point to last element"
            return True
        
        def test_tail_remove_tail():
            ll_tail.remove_ingredient(103)
            assert ll_tail.tail is not None, "Tail should not be None after removing tail"
            assert ll_tail.tail.ingredient.ingredient_id == 102, "Tail should update to new last element"
            return True
        
        def test_tail_remove_all():
            ll_tail.remove_ingredient(102)
            assert ll_tail.tail is None, "Tail should be None after removing all"
            assert ll_tail.head is None, "Head should be None after removing all"
            return True
        
        def test_tail_insert_complexity():
            ll_complex = RecipeIngredientLinkedList()
            for i in range(1000):
                ing = Ingredient(i, f"ing{i}", IngredientCategory.GRAIN, "kg", 10.0, 5.0, 3)
                ll_complex.add_ingredient(ing, 1.0)
            assert ll_complex.tail.ingredient.ingredient_id == 999, "Tail should point to last of 1000 elements"
            assert ll_complex.size == 1000, "Size should be 1000"
            return True
        
        tail_test_cases = [
            ("tail_after_add", test_tail_add, "Tail pointer after add (尾指针添加后)"),
            ("tail_single_node", test_tail_single_node, "Tail equals head for single node (单节点时首尾相同)"),
            ("tail_after_remove_head", test_tail_remove_head, "Tail after remove head (移除头部后尾指针)"),
            ("tail_after_remove_tail", test_tail_remove_tail, "Tail updates after remove tail (移除尾部后更新)"),
            ("tail_after_remove_all", test_tail_remove_all, "Tail is None after remove all (移除全部后为空)"),
            ("tail_insert_O1", test_tail_insert_complexity, "Insert 1000 elements with tail (O(1)插入验证)"),
        ]
        
        for func_name, test_func, desc in tail_test_cases:
            total_tests += 1
            passed, msg = run_single_function_test(func_name, test_func, desc)
            if passed:
                passed_tests += 1
            else:
                all_passed = False
            test_result.insert(tk.END, msg + "\n")
            test_result.update()
        
        for func_name, test_func, desc in test_cases:
            total_tests += 1
            passed, msg = run_single_function_test(func_name, test_func, desc)
            if passed:
                passed_tests += 1
            else:
                all_passed = False
            test_result.insert(tk.END, msg + "\n")
            test_result.update()
        
        test_result.insert(tk.END, "\n--- BST Operations (BST操作) ---\n")
        
        test_cases = [
            ("bst_search", lambda: bst.search(all_recipes[0].name), "Search existing recipe"),
            ("bst_search_non_exist", lambda: bst.search("NonExistRecipe"), "Search non-existent recipe"),
            ("bst_in_order", lambda: bst.in_order(), "In-order traversal"),
            ("bst_get_recipes_by_cuisine", lambda: bst.get_recipes_by_cuisine("CHINESE"), "Filter by cuisine"),
            ("bst_range_search", lambda: bst.range_search("A", "F"), "Alphabet range search"),
            ("bst_get_all_feasible", lambda: bst.get_all_feasible_recipes(), "Get feasible recipes"),
            ("bst_get_height", lambda: bst.get_height(), "Get BST height"),
        ]
        
        for func_name, test_func, desc in test_cases:
            total_tests += 1
            passed, msg = run_single_function_test(func_name, test_func, desc)
            if passed:
                passed_tests += 1
            else:
                all_passed = False
            test_result.insert(tk.END, msg + "\n")
            test_result.update()
        
        test_result.insert(tk.END, "\n--- Heap Operations (堆操作) ---\n")
        
        test_cases = [
            ("heap_size", lambda: heap.size(), "Heap size"),
            ("heap_get_top_k", lambda: heap.get_top_k(10), "Get Top10"),
            ("heap_pop_highest", lambda: heap.pop_highest(), "Pop highest priority"),
            ("heap_push", lambda: heap.push(ing1, 0.5), "Push new ingredient"),
        ]
        
        for func_name, test_func, desc in test_cases:
            total_tests += 1
            passed, msg = run_single_function_test(func_name, test_func, desc)
            if passed:
                passed_tests += 1
            else:
                all_passed = False
            test_result.insert(tk.END, msg + "\n")
            test_result.update()
        
        test_result.insert(tk.END, "\n--- Supply Graph Operations (供应图操作) ---\n")
        
        first_sid = list(supply_graph.adj.keys())[0] if supply_graph.adj else 0
        first_ing_id = list(supply_graph.adj[first_sid].keys())[0] if first_sid in supply_graph.adj and supply_graph.adj[first_sid] else 0
        
        test_cases = [
            ("graph_get_suppliers", lambda: supply_graph.get_suppliers_for_ingredient(1), "Get ingredient suppliers"),
            ("graph_get_unit_cost", lambda: supply_graph.get_unit_cost(first_sid, first_ing_id), "Get unit cost"),
            ("graph_get_cheapest", lambda: supply_graph.get_cheapest_supplier(1), "Get cheapest supplier"),
            ("graph_get_ingredients_under_budget", lambda: supply_graph.get_ingredients_under_budget(10.0), "Ingredients under budget"),
            ("graph_add_supplier", lambda: supply_graph.add_supplier(99), "Add supplier"),
            ("graph_remove_supplier", lambda: supply_graph.remove_supplier(99), "Remove supplier"),
        ]
        
        for func_name, test_func, desc in test_cases:
            total_tests += 1
            passed, msg = run_single_function_test(func_name, test_func, desc)
            if passed:
                passed_tests += 1
            else:
                all_passed = False
            test_result.insert(tk.END, msg + "\n")
            test_result.update()
        
        test_result.insert(tk.END, "\n" + "=" * 80 + "\n")
        test_result.insert(tk.END, "[Part2 - Advanced Algorithms (高级算法)]\n")
        test_result.insert(tk.END, "=" * 80 + "\n\n")
        
        test_result.insert(tk.END, "--- Substitution Graph Operations (替换图操作) ---\n")
        
        test_cases = [
            ("sub_get_all_substitutes", lambda: sub_graph.get_all_substitutes(4), "Get all substitutes"),
            ("sub_register_ingredient", lambda: sub_graph.register_ingredient(Ingredient(999, "test", IngredientCategory.GRAIN, "kg", 1.0, 1.0, 1)), "Register ingredient"),
            ("sub_add_substitution", lambda: sub_graph.add_substitution_pair(999, 1, 0.5), "Add substitution"),
        ]
        
        for func_name, test_func, desc in test_cases:
            total_tests += 1
            passed, msg = run_single_function_test(func_name, test_func, desc)
            if passed:
                passed_tests += 1
            else:
                all_passed = False
            test_result.insert(tk.END, msg + "\n")
            test_result.update()
        
        test_result.insert(tk.END, "\n--- Supplier Optimization (供应商优化) ---\n")
        
        from src.part2.supplier_optimizer import SupplierOptimizer
        opt = SupplierOptimizer(supply_graph)
        
        test_cases = [
            ("opt_add_supplier", lambda: opt.add_supplier(Supplier(1, "Test", "Beijing", 0.9)), "Add supplier"),
            ("opt_get_min_cost", lambda: opt.get_min_cost_supplier_set(all_recipes[0], 0.6), "Get min cost supplier"),
        ]
        
        for func_name, test_func, desc in test_cases:
            total_tests += 1
            passed, msg = run_single_function_test(func_name, test_func, desc)
            if passed:
                passed_tests += 1
            else:
                all_passed = False
            test_result.insert(tk.END, msg + "\n")
            test_result.update()
        
        test_result.insert(tk.END, "\n--- Menu Planning (菜单规划) ---\n")
        
        from src.part2.menu_planner import WeeklyMenuPlanner
        planner = WeeklyMenuPlanner(bst, heap, supply_graph)
        
        test_cases = [
            ("planner_analyze_menu", lambda: planner.analyze_menu(all_recipes[:3]), "Analyze menu"),
            ("planner_generate_plan", lambda: planner.generate_procurement_plan(), "Generate procurement plan"),
        ]
        
        for func_name, test_func, desc in test_cases:
            total_tests += 1
            passed, msg = run_single_function_test(func_name, test_func, desc)
            if passed:
                passed_tests += 1
            else:
                all_passed = False
            test_result.insert(tk.END, msg + "\n")
            test_result.update()
        
        test_result.insert(tk.END, "\n" + "=" * 80 + "\n")
        test_result.insert(tk.END, "[Part3 - Crisis Recovery (危机恢复)]\n")
        test_result.insert(tk.END, "=" * 80 + "\n\n")
        
        from src.part3.crisis_recovery import SupplyCrisisRecovery
        crisis = SupplyCrisisRecovery(supply_graph, bst, sub_graph)
        
        test_cases = [
            ("crisis_simulate_shutdown", lambda: crisis.simulate_supplier_shutdown(1), "Simulate supplier shutdown"),
            ("crisis_report_risk", lambda: crisis.report_risk_recipes(), "Report risk recipes"),
            ("crisis_generate_recovery", lambda: crisis.generate_recovery_plan(), "Generate recovery plan"),
        ]
        
        for func_name, test_func, desc in test_cases:
            total_tests += 1
            passed, msg = run_single_function_test(func_name, test_func, desc)
            if passed:
                passed_tests += 1
            else:
                all_passed = False
            test_result.insert(tk.END, msg + "\n")
            test_result.update()
        
        progress_bar.stop()
        
        test_result.insert(tk.END, "\n" + "=" * 80 + "\n")
        test_result.insert(tk.END, "[Test Summary (测试总结)]\n")
        test_result.insert(tk.END, f"Total tests: {total_tests}\n")
        test_result.insert(tk.END, f"Passed: {passed_tests}\n")
        test_result.insert(tk.END, f"Failed: {total_tests - passed_tests}\n")
        test_result.insert(tk.END, "-" * 80 + "\n")
        
        if all_passed:
            test_result.insert(tk.END, "[right] All tests passed! System running normally!\n")
        else:
            test_result.insert(tk.END, "[error] Some tests failed, please check the code!\n")
        
        test_result.insert(tk.END, "=" * 80 + "\n")
    
    ttk.Button(tab7, text="Run All Tests", command=run_all_tests).pack(pady=10)

    # Tab8: Data Management (数据管理)
    from src.part1.models import Ingredient, IngredientCategory, CuisineType, Difficulty, Supplier
    from src.part1.linked_list import RecipeIngredientLinkedList

    mgmt_notebook = ttk.Notebook(tab8)
    mgmt_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    mgmt_tab1 = ttk.Frame(mgmt_notebook)
    mgmt_tab2 = ttk.Frame(mgmt_notebook)
    mgmt_tab3 = ttk.Frame(mgmt_notebook)
    mgmt_tab4 = ttk.Frame(mgmt_notebook)

    mgmt_notebook.add(mgmt_tab1, text="Recipe Management (食谱管理)")
    mgmt_notebook.add(mgmt_tab2, text="Ingredient Management (食材管理)")
    mgmt_notebook.add(mgmt_tab3, text="Supplier Management (供应商管理)")
    mgmt_notebook.add(mgmt_tab4, text="Substitution Management (替换管理)")

    def refresh_all_recipes():
        nonlocal all_recipes
        all_recipes = bst.in_order()

    # Tab8.1: Recipe Management
    ttk.Label(mgmt_tab1, text="Add New Recipe (添加新食谱):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    
    ttk.Label(mgmt_tab1, text="Name (名称):").grid(row=1, column=0, padx=5, pady=3, sticky="w")
    new_recipe_name = ttk.Entry(mgmt_tab1, width=20)
    new_recipe_name.grid(row=1, column=1, padx=5, pady=3)

    ttk.Label(mgmt_tab1, text="Cuisine (菜系):").grid(row=1, column=2, padx=5, pady=3, sticky="w")
    recipe_cuisine_var = tk.StringVar()
    recipe_cuisine_combo = ttk.Combobox(mgmt_tab1, textvariable=recipe_cuisine_var, width=15)
    recipe_cuisine_combo['values'] = ('CHINESE', 'WESTERN', 'JAPANESE', 'THAI')
    recipe_cuisine_combo.current(0)
    recipe_cuisine_combo.grid(row=1, column=3, padx=5, pady=3)

    ttk.Label(mgmt_tab1, text="Difficulty (难度):").grid(row=1, column=4, padx=5, pady=3, sticky="w")
    recipe_diff_var = tk.StringVar()
    recipe_diff_combo = ttk.Combobox(mgmt_tab1, textvariable=recipe_diff_var, width=10)
    recipe_diff_combo['values'] = ('EASY', 'MEDIUM', 'HARD')
    recipe_diff_combo.current(1)
    recipe_diff_combo.grid(row=1, column=5, padx=5, pady=3)

    ttk.Label(mgmt_tab1, text="Prep Time (min):").grid(row=2, column=0, padx=5, pady=3, sticky="w")
    recipe_time = ttk.Entry(mgmt_tab1, width=10)
    recipe_time.grid(row=2, column=1, padx=5, pady=3)
    recipe_time.insert(0, "30")

    ttk.Label(mgmt_tab1, text="Servings (人数):").grid(row=2, column=2, padx=5, pady=3, sticky="w")
    recipe_servings = ttk.Entry(mgmt_tab1, width=10)
    recipe_servings.grid(row=2, column=3, padx=5, pady=3)
    recipe_servings.insert(0, "4")

    def add_recipe():
        try:
            name = new_recipe_name.get().strip()
            if not name:
                messagebox.showwarning("Warning", "Please enter recipe name (请输入食谱名称)")
                return
            cuisine = CuisineType(recipe_cuisine_var.get())
            difficulty = Difficulty(recipe_diff_var.get())
            prep_time = int(recipe_time.get())
            servings = int(recipe_servings.get())
            
            new_recipe = Recipe(len(all_recipes) + 100, name, cuisine, difficulty, prep_time, servings)
            new_recipe.ingredient_list = RecipeIngredientLinkedList()
            bst.insert(new_recipe)
            refresh_all_recipes()
            messagebox.showinfo("Success", f"Recipe '{name}' added successfully (食谱'{name}'添加成功)")
            new_recipe_name.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add recipe: {str(e)}")

    ttk.Button(mgmt_tab1, text="Add Recipe (添加食谱)", command=add_recipe).grid(row=2, column=4, padx=10, pady=5)

    ttk.Label(mgmt_tab1, text="Delete Recipe (删除食谱):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    del_recipe_name = ttk.Entry(mgmt_tab1, width=30)
    del_recipe_name.grid(row=3, column=1, padx=5, pady=3)
    del_recipe_name.insert(0, "Enter recipe name to delete (输入要删除的食谱名称)")

    def delete_recipe():
        name = del_recipe_name.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter recipe name (请输入食谱名称)")
            return
        deleted = bst.delete(name)
        if deleted:
            refresh_all_recipes()
            messagebox.showinfo("Success", f"Recipe '{name}' deleted successfully (食谱'{name}'删除成功)")
        else:
            messagebox.showinfo("Info", f"Recipe '{name}' not found (食谱'{name}'未找到)")

    ttk.Button(mgmt_tab1, text="Delete Recipe (删除食谱)", command=delete_recipe).grid(row=3, column=2, padx=10, pady=5)

    ttk.Label(mgmt_tab1, text="Current Recipes (当前食谱列表):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
    recipe_list = tk.Listbox(mgmt_tab1, width=80, height=10)
    recipe_list.grid(row=5, column=0, columnspan=6, padx=10, pady=5)

    def update_recipe_list():
        recipe_list.delete(0, tk.END)
        for r in bst.in_order():
            recipe_list.insert(tk.END, f"{r.name} | {r.cuisine_type.value} | {r.difficulty.value}")

    ttk.Button(mgmt_tab1, text="Refresh List (刷新列表)", command=update_recipe_list).grid(row=6, column=0, padx=10, pady=5)
    update_recipe_list()

    # Tab8.2: Ingredient Management
    ttk.Label(mgmt_tab2, text="Add New Ingredient (添加新食材):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    
    ttk.Label(mgmt_tab2, text="Name (名称):").grid(row=1, column=0, padx=5, pady=3, sticky="w")
    new_ing_name = ttk.Entry(mgmt_tab2, width=15)
    new_ing_name.grid(row=1, column=1, padx=5, pady=3)

    ttk.Label(mgmt_tab2, text="Category (分类):").grid(row=1, column=2, padx=5, pady=3, sticky="w")
    ing_category_var = tk.StringVar()
    ing_category_combo = ttk.Combobox(mgmt_tab2, textvariable=ing_category_var, width=12)
    ing_category_combo['values'] = ('PRODUCE', 'DAIRY', 'MEAT', 'GRAIN', 'SPICE', 'LIQUID')
    ing_category_combo.current(0)
    ing_category_combo.grid(row=1, column=3, padx=5, pady=3)

    ttk.Label(mgmt_tab2, text="Unit (单位):").grid(row=1, column=4, padx=5, pady=3, sticky="w")
    ing_unit = ttk.Entry(mgmt_tab2, width=5)
    ing_unit.grid(row=1, column=5, padx=5, pady=3)
    ing_unit.insert(0, "kg")

    ttk.Label(mgmt_tab2, text="Current Stock (当前库存):").grid(row=2, column=0, padx=5, pady=3, sticky="w")
    ing_current_stock = ttk.Entry(mgmt_tab2, width=10)
    ing_current_stock.grid(row=2, column=1, padx=5, pady=3)
    ing_current_stock.insert(0, "10.0")

    ttk.Label(mgmt_tab2, text="Min Stock (最低库存):").grid(row=2, column=2, padx=5, pady=3, sticky="w")
    ing_min_stock = ttk.Entry(mgmt_tab2, width=10)
    ing_min_stock.grid(row=2, column=3, padx=5, pady=3)
    ing_min_stock.insert(0, "5.0")

    def add_ingredient():
        try:
            name = new_ing_name.get().strip()
            if not name:
                messagebox.showwarning("Warning", "Please enter ingredient name (请输入食材名称)")
                return
            category = IngredientCategory(ing_category_var.get())
            unit = ing_unit.get().strip()
            current_stock = float(ing_current_stock.get())
            min_stock = float(ing_min_stock.get())
            
            new_id = max([ing.ingredient_id for ing in sub_graph.ingredient_map.values()], default=0) + 1
            new_ing = Ingredient(new_id, name, category, unit, current_stock, min_stock)
            sub_graph.register_ingredient(new_ing)
            heap.push(new_ing, 1)
            messagebox.showinfo("Success", f"Ingredient '{name}' added successfully (食材'{name}'添加成功)")
            new_ing_name.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add ingredient: {str(e)}")

    ttk.Button(mgmt_tab2, text="Add Ingredient (添加食材)", command=add_ingredient).grid(row=2, column=4, padx=10, pady=5)

    ttk.Label(mgmt_tab2, text="Current Ingredients (当前食材列表):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    ing_list = tk.Listbox(mgmt_tab2, width=80, height=10)
    ing_list.grid(row=4, column=0, columnspan=6, padx=10, pady=5)

    def update_ingredient_list():
        ing_list.delete(0, tk.END)
        for ing in sub_graph.ingredient_map.values():
            ing_list.insert(tk.END, f"ID:{ing.ingredient_id} | {ing.name} | {ing.category.value} | Stock: {ing.current_stock}/{ing.minimum_stock}{ing.unit}")

    ttk.Button(mgmt_tab2, text="Refresh List (刷新列表)", command=update_ingredient_list).grid(row=5, column=0, padx=10, pady=5)
    update_ingredient_list()

    # Tab8.3: Supplier Management
    ttk.Label(mgmt_tab3, text="Add New Supplier (添加新供应商):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    
    ttk.Label(mgmt_tab3, text="Name (名称):").grid(row=1, column=0, padx=5, pady=3, sticky="w")
    new_sup_name = ttk.Entry(mgmt_tab3, width=20)
    new_sup_name.grid(row=1, column=1, padx=5, pady=3)

    ttk.Label(mgmt_tab3, text="Location (位置):").grid(row=1, column=2, padx=5, pady=3, sticky="w")
    sup_location = ttk.Entry(mgmt_tab3, width=15)
    sup_location.grid(row=1, column=3, padx=5, pady=3)
    sup_location.insert(0, "Beijing")

    ttk.Label(mgmt_tab3, text="Reliability (0-1):").grid(row=1, column=4, padx=5, pady=3, sticky="w")
    sup_reliability = ttk.Entry(mgmt_tab3, width=10)
    sup_reliability.grid(row=1, column=5, padx=5, pady=3)
    sup_reliability.insert(0, "0.85")

    def add_supplier():
        try:
            name = new_sup_name.get().strip()
            if not name:
                messagebox.showwarning("Warning", "Please enter supplier name (请输入供应商名称)")
                return
            location = sup_location.get().strip()
            reliability = float(sup_reliability.get())
            
            new_id = max(list(supply_graph.adj.keys()), default=0) + 1
            supply_graph.add_supplier(new_id)
            messagebox.showinfo("Success", f"Supplier '{name}' added successfully (供应商'{name}'添加成功)")
            new_sup_name.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add supplier: {str(e)}")

    ttk.Button(mgmt_tab3, text="Add Supplier (添加供应商)", command=add_supplier).grid(row=1, column=6, padx=10, pady=5)

    ttk.Label(mgmt_tab3, text="Add Supply Relationship (添加供应关系):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    
    ttk.Label(mgmt_tab3, text="Supplier ID:").grid(row=3, column=0, padx=5, pady=3, sticky="w")
    sr_supplier_id = ttk.Entry(mgmt_tab3, width=8)
    sr_supplier_id.grid(row=3, column=1, padx=5, pady=3)

    ttk.Label(mgmt_tab3, text="Ingredient ID:").grid(row=3, column=2, padx=5, pady=3, sticky="w")
    sr_ingredient_id = ttk.Entry(mgmt_tab3, width=8)
    sr_ingredient_id.grid(row=3, column=3, padx=5, pady=3)

    ttk.Label(mgmt_tab3, text="Cost per Unit:").grid(row=3, column=4, padx=5, pady=3, sticky="w")
    sr_cost = ttk.Entry(mgmt_tab3, width=10)
    sr_cost.grid(row=3, column=5, padx=5, pady=3)
    sr_cost.insert(0, "10.0")

    def add_supply_relation():
        try:
            sid = int(sr_supplier_id.get())
            iid = int(sr_ingredient_id.get())
            cost = float(sr_cost.get())
            
            supply_graph.add_supply_relation(sid, iid, cost)
            messagebox.showinfo("Success", f"Supply relationship added (供应关系添加成功)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add supply relationship: {str(e)}")

    ttk.Button(mgmt_tab3, text="Add Relation (添加关系)", command=add_supply_relation).grid(row=3, column=6, padx=10, pady=5)

    ttk.Label(mgmt_tab3, text="Delete Supplier (删除供应商):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
    del_sup_id = ttk.Entry(mgmt_tab3, width=15)
    del_sup_id.grid(row=4, column=1, padx=5, pady=3)
    del_sup_id.insert(0, "Enter supplier ID")

    def delete_supplier():
        try:
            sid = int(del_sup_id.get())
            supply_graph.remove_supplier(sid)
            messagebox.showinfo("Success", f"Supplier {sid} deleted (供应商{sid}删除成功)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete supplier: {str(e)}")

    ttk.Button(mgmt_tab3, text="Delete Supplier (删除供应商)", command=delete_supplier).grid(row=4, column=2, padx=10, pady=5)

    ttk.Label(mgmt_tab3, text="Current Suppliers (当前供应商列表):").grid(row=5, column=0, padx=10, pady=5, sticky="w")
    sup_list = tk.Listbox(mgmt_tab3, width=80, height=10)
    sup_list.grid(row=6, column=0, columnspan=7, padx=10, pady=5)

    def update_supplier_list():
        sup_list.delete(0, tk.END)
        for sid in supply_graph.adj:
            sup_list.insert(tk.END, f"Supplier ID: {sid}")

    ttk.Button(mgmt_tab3, text="Refresh List (刷新列表)", command=update_supplier_list).grid(row=7, column=0, padx=10, pady=5)
    update_supplier_list()

    # Tab8.4: Substitution Management
    ttk.Label(mgmt_tab4, text="Add Substitution Pair (添加替换关系):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    
    ttk.Label(mgmt_tab4, text="Ingredient A ID:").grid(row=1, column=0, padx=5, pady=3, sticky="w")
    sub_a_id = ttk.Entry(mgmt_tab4, width=8)
    sub_a_id.grid(row=1, column=1, padx=5, pady=3)

    ttk.Label(mgmt_tab4, text="Ingredient B ID:").grid(row=1, column=2, padx=5, pady=3, sticky="w")
    sub_b_id = ttk.Entry(mgmt_tab4, width=8)
    sub_b_id.grid(row=1, column=3, padx=5, pady=3)

    ttk.Label(mgmt_tab4, text="Quality Score (0-1):").grid(row=1, column=4, padx=5, pady=3, sticky="w")
    sub_quality = ttk.Entry(mgmt_tab4, width=10)
    sub_quality.grid(row=1, column=5, padx=5, pady=3)
    sub_quality.insert(0, "0.8")

    def add_substitution():
        try:
            a_id = int(sub_a_id.get())
            b_id = int(sub_b_id.get())
            quality = float(sub_quality.get())
            
            if a_id not in sub_graph.ingredient_map:
                messagebox.showwarning("Warning", f"Ingredient ID {a_id} not found (食材ID{a_id}未找到)")
                return
            if b_id not in sub_graph.ingredient_map:
                messagebox.showwarning("Warning", f"Ingredient ID {b_id} not found (食材ID{b_id}未找到)")
                return
            
            sub_graph.add_substitution_pair(a_id, b_id, quality)
            messagebox.showinfo("Success", f"Substitution pair added (替换关系添加成功)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add substitution: {str(e)}")

    ttk.Button(mgmt_tab4, text="Add Substitution (添加替换)", command=add_substitution).grid(row=1, column=6, padx=10, pady=5)

    ttk.Label(mgmt_tab4, text="Current Substitution Relationships (当前替换关系):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    sub_list = tk.Listbox(mgmt_tab4, width=80, height=10)
    sub_list.grid(row=3, column=0, columnspan=7, padx=10, pady=5)

    def update_substitution_list():
        sub_list.delete(0, tk.END)
        seen_pairs = set()
        for ing_id, subs in sub_graph.sub_edges.items():
            for target_id, score in subs:
                if ing_id < target_id:
                    pair = (ing_id, target_id)
                    if pair not in seen_pairs:
                        seen_pairs.add(pair)
                        ing_a = sub_graph.ingredient_map.get(ing_id, None)
                        ing_b = sub_graph.ingredient_map.get(target_id, None)
                        name_a = ing_a.name if ing_a else f"ID:{ing_id}"
                        name_b = ing_b.name if ing_b else f"ID:{target_id}"
                        sub_list.insert(tk.END, f"{name_a} <-> {name_b} | Quality: {score:.2f}")

    ttk.Button(mgmt_tab4, text="Refresh List (刷新列表)", command=update_substitution_list).grid(row=4, column=0, padx=10, pady=5)
    update_substitution_list()

    # Tab9: Structure Visualization (结构可视化)
    viz_notebook = ttk.Notebook(tab9)
    viz_tab1 = ttk.Frame(viz_notebook)
    viz_tab2 = ttk.Frame(viz_notebook)
    viz_tab3 = ttk.Frame(viz_notebook)
    viz_tab4 = ttk.Frame(viz_notebook)
    viz_notebook.add(viz_tab1, text="Supply Graph (供应网络图)")
    viz_notebook.add(viz_tab2, text="Heap Tree (堆树)")
    viz_notebook.add(viz_tab3, text="BST Tree (BST树)")
    viz_notebook.add(viz_tab4, text="Linked List (链表)")
    viz_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    from PIL import Image, ImageTk
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    
    plt.rcParams["font.sans-serif"] = ["SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["mathtext.fontset"] = "dejavusans"
    
    def create_visualization_container(parent, draw_func, default_size=(10, 6)):
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=3)
        
        zoom_label = ttk.Label(control_frame, text="Zoom: 100%")
        zoom_label.pack(side=tk.RIGHT, padx=10)
        
        ttk.Button(control_frame, text="Zoom In (+)", command=lambda: zoom(1.2)).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Zoom Out (-)", command=lambda: zoom(0.8)).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Reset", command=lambda: zoom(1.0)).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Refresh", command=lambda: zoom(1.0)).pack(side=tk.LEFT, padx=5)
        
        scroll_frame = ttk.Frame(parent)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        v_scrollbar = ttk.Scrollbar(scroll_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(scroll_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        canvas = tk.Canvas(scroll_frame, bg="white", width=800, height=500,
                           yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        v_scrollbar.config(command=canvas.yview)
        h_scrollbar.config(command=canvas.xview)
        
        current_scale = 1.0
        current_img = None
        last_fig = None
        
        def zoom(factor):
            nonlocal current_scale, current_img, last_fig
            new_scale = max(0.25, min(3.0, current_scale * factor))
            current_scale = new_scale
            zoom_label.config(text=f"Zoom: {int(current_scale * 100)}%")
            render_plot()
        
        def render_plot():
            nonlocal current_img, last_fig
            
            if last_fig:
                plt.close(last_fig)
            
            fig, ax = plt.subplots(figsize=(default_size[0] * current_scale, default_size[1] * current_scale), dpi=100)
            
            draw_func(ax)
            
            fig.tight_layout()
            
            import io
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            img = Image.open(buf)
            current_img = ImageTk.PhotoImage(img)
            w, h = img.size
            
            canvas.delete("all")
            canvas.create_image(0, 0, anchor=tk.NW, image=current_img)
            canvas.config(scrollregion=(0, 0, w, h))
            
            last_fig = fig
        
        render_plot()
        
        return canvas
    
    def draw_supply_graph(ax):
        ax.set_title("Supply Network Graph (供应网络图)", fontsize=14, pad=20)
        
        suppliers = list(supply_graph.adj.keys())
        ingredients = list(supply_graph.ingredient_to_suppliers.keys())
        
        n_suppliers = len(suppliers)
        n_ingredients = len(ingredients)
        
        if n_suppliers == 0 and n_ingredients == 0:
            ax.text(0.5, 0.5, "No supply data (无供应数据)", ha='center', va='center', fontsize=14)
            ax.axis('off')
            return
        
        supplier_pos = {}
        ingredient_pos = {}
        y_sup = 0.8
        y_ing = 0.2
        
        max_items = max(n_suppliers, n_ingredients)
        if max_items > 15:
            margin = 0.05
        else:
            margin = 0.1
        
        if n_suppliers > 0:
            if n_suppliers == 1:
                supplier_pos[suppliers[0]] = (0.5, y_sup)
            else:
                cols = min(n_suppliers, 5)
                rows = (n_suppliers + cols - 1) // cols
                x_step = (1 - 2 * margin) / cols
                y_step = 0.15
                
                for i, sid in enumerate(suppliers):
                    col = i % cols
                    row = i // cols
                    x = margin + col * x_step + x_step / 2
                    y = y_sup - row * y_step
                    supplier_pos[sid] = (x, y)
        
        if n_ingredients > 0:
            if n_ingredients == 1:
                ingredient_pos[ingredients[0]] = (0.5, y_ing)
            else:
                cols = min(n_ingredients, 5)
                rows = (n_ingredients + cols - 1) // cols
                x_step = (1 - 2 * margin) / cols
                y_step = 0.15
                
                for i, iid in enumerate(ingredients):
                    col = i % cols
                    row = i // cols
                    x = margin + col * x_step + x_step / 2
                    y = y_ing + row * y_step
                    ingredient_pos[iid] = (x, y)
        
        node_size = max(200, min(500, 2000 / max(n_suppliers, n_ingredients, 1)))
        
        for sid in suppliers:
            ax.scatter(supplier_pos[sid][0], supplier_pos[sid][1], s=node_size, c='#636E72', edgecolors='#2D3436', 
                       zorder=5, marker='s')
            ax.text(supplier_pos[sid][0], supplier_pos[sid][1], f'S{sid}', fontsize=min(10, 200 / max_items), 
                    ha='center', va='center', fontweight='bold', color='white')
        
        for iid in ingredients:
            ax.scatter(ingredient_pos[iid][0], ingredient_pos[iid][1], s=node_size, c='#00B894', edgecolors='#00CEC9', 
                       zorder=5, marker='o')
            ax.text(ingredient_pos[iid][0], ingredient_pos[iid][1], f'I{iid}', fontsize=min(10, 200 / max_items), 
                    ha='center', va='center', fontweight='bold', color='white')
        
        label_positions = []
        label_idx = 0
        
        for sid in suppliers:
            for iid, cost in supply_graph.adj.get(sid, {}).items():
                sx, sy = supplier_pos[sid]
                ix, iy = ingredient_pos[iid]
                
                mid_x = (sx + ix) / 2
                mid_y = (sy + iy) / 2
                
                ax.plot([sx, ix], [sy, iy], '#B2BEC3', linewidth=1.2, alpha=0.7)
                
                label_y_offset = (label_idx % 3 - 1) * 0.03
                label_x_offset = ((label_idx // 3) % 3 - 1) * 0.04
                label_x = mid_x + label_x_offset
                label_y = mid_y + label_y_offset + 0.02
                
                overlap = False
                for px, py in label_positions:
                    if abs(label_x - px) < 0.05 and abs(label_y - py) < 0.03:
                        overlap = True
                        break
                
                if not overlap and 0.05 < label_x < 0.95 and 0.05 < label_y < 0.95:
                    ax.text(label_x, label_y, f'{cost:.1f}', fontsize=6, color='#E17055', fontweight='bold',
                            bbox=dict(facecolor='white', edgecolor='none', alpha=0.9, pad=0.5))
                    label_positions.append((label_x, label_y))
                label_idx += 1
        
        ax.text(0.5, 0.96, f"Suppliers: {n_suppliers} | Ingredients: {n_ingredients}", 
                ha='center', va='center', fontsize=10, color='#636E72')
        
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#636E72', edgecolor='#2D3436', label='Supplier'),
            Patch(facecolor='#00B894', edgecolor='#00CEC9', label='Ingredient')
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.95, 0.95), 
                  ncol=1, fontsize=9, frameon=True, edgecolor='lightgray')
        
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        ax.axis('off')
    
    def draw_heap(ax):
        ax.set_title("Procurement Heap (采购堆 - 最大堆)", fontsize=14, pad=20)
        
        heap_items = heap.heap
        n = len(heap_items)
        
        if n == 0:
            ax.text(0.5, 0.5, "Heap is empty (堆为空)", ha='center', va='center', fontsize=14)
            ax.axis('off')
            return
        
        max_urgency = max(item[0] for item in heap_items) if heap_items else 1
        min_urgency = min(item[0] for item in heap_items) if heap_items else 0
        urgency_range = max_urgency - min_urgency if max_urgency != min_urgency else 1
        
        levels = []
        level = [0]
        while level:
            levels.append(level)
            next_level = []
            for i in level:
                left = 2 * i + 1
                right = 2 * i + 2
                if left < n:
                    next_level.append(left)
                if right < n:
                    next_level.append(right)
            level = next_level
        
        max_level = len(levels)
        y_step = 0.8 / max_level
        y_start = 0.9
        
        pos = {}
        for l_idx, level in enumerate(levels):
            y = y_start - l_idx * y_step
            level_width = min(1.0, 0.9 / (2 ** l_idx))
            x_start = 0.5 - level_width / 2
            x_step = level_width / max(len(level) - 1, 1) if len(level) > 1 else 0
            for i, idx in enumerate(level):
                if len(level) == 1:
                    x = 0.5
                else:
                    x = x_start + i * x_step
                pos[idx] = (x, y)
        
        for idx in range(n):
            urgency, ing = heap_items[idx]
            norm_urgency = (urgency - min_urgency) / urgency_range
            r = int(255 * norm_urgency)
            g = int(255 * (1 - norm_urgency))
            b = int(80 * (1 - norm_urgency))
            color = f'#{r:02X}{g:02X}{b:02X}'
            
            node_size = 350 if idx == 0 else 280
            ax.scatter(pos[idx][0], pos[idx][1], s=node_size, c=color, 
                       edgecolors='#2D3436', zorder=5)
            
            ax.text(pos[idx][0], pos[idx][1] - 0.02, f'ID:{idx}', fontsize=7, ha='center', va='top', color='#636E72')
            ax.text(pos[idx][0], pos[idx][1], f'{urgency:.0f}', fontsize=10, ha='center', va='center', 
                    fontweight='bold', color='white')
            ax.text(pos[idx][0], pos[idx][1] + 0.025, f'{ing.name[:5]}', fontsize=7, ha='center', va='bottom', color='#2D3436')
            
            if idx == 0:
                ax.scatter(pos[idx][0], pos[idx][1] + 0.06, s=100, c='#E17055', marker='*', zorder=10)
                ax.text(pos[idx][0], pos[idx][1] + 0.09, 'ROOT', fontsize=7, ha='center', va='bottom', color='#E17055', fontweight='bold')
            
            left = 2 * idx + 1
            right = 2 * idx + 2
            if left < n:
                ax.plot([pos[idx][0], pos[left][0]], [pos[idx][1], pos[left][1]], '#636E72', linewidth=2)
            if right < n:
                ax.plot([pos[idx][0], pos[right][0]], [pos[idx][1], pos[right][1]], '#636E72', linewidth=2)
        
        ax.text(0.5, 0.97, f"Size: {n} | Max Urgency: {max_urgency:.1f}", 
                ha='center', va='center', fontsize=10, color='#636E72')
        
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#FF5533', edgecolor='#2D3436', label='High Urgency'),
            Patch(facecolor='#88CC88', edgecolor='#2D3436', label='Low Urgency'),
            Patch(facecolor='#E17055', label='Root')
        ]
        ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.08), 
                  ncol=3, fontsize=9, frameon=True, edgecolor='lightgray')
        
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.15, 1.1)
        ax.axis('off')
    
    def draw_bst(ax):
        ax.set_title("Recipe BST (食谱二叉搜索树)", fontsize=14, pad=20)
        
        node_list = []
        node_info = {}
        node_id = 0
        
        def get_height(node):
            if not node:
                return 0
            return 1 + max(get_height(node.left), get_height(node.right))
        
        height = get_height(bst.root)
        
        def allocate_positions(node, x_start, x_end, y):
            nonlocal node_id
            if not node:
                return 0, None
            
            node_id += 1
            node_idx = node_id - 1
            node_list.append(node)
            node_info[node] = {'id': node_idx}
            
            if not node.left and not node.right:
                x = (x_start + x_end) / 2
                node_info[node]['pos'] = (x, y)
                return 1, x
            
            mid = (x_start + x_end) / 2
            left_width = (mid - x_start) * 0.8
            right_width = (x_end - mid) * 0.8
            
            left_count, left_center = allocate_positions(node.left, x_start, mid, y - 0.12)
            right_count, right_center = allocate_positions(node.right, mid, x_end, y - 0.12)
            
            if left_center is None:
                x = right_center
            elif right_center is None:
                x = left_center
            else:
                x = (left_center + right_center) / 2
            
            node_info[node]['pos'] = (x, y)
            return left_count + right_count + 1, x
        
        if bst.root:
            allocate_positions(bst.root, 0.05, 0.95, 0.9)
        
        if not node_list:
            ax.text(0.5, 0.5, "BST is empty (BST为空)", ha='center', va='center', fontsize=14)
            ax.axis('off')
            return
        
        drawn_nodes = set()
        
        def draw_tree(node):
            if not node or node in drawn_nodes:
                return
            drawn_nodes.add(node)
            x, y = node_info[node]['pos']
            node_idx = node_info[node]['id']
            
            color = '#FDCB6E'
            edge_color = '#E67E22'
            
            ax.scatter(x, y, s=350, c=color, edgecolors=edge_color, zorder=5)
            ax.text(x, y - 0.02, f'#{node_idx}', fontsize=7, ha='center', va='top', color='#636E72')
            ax.text(x, y, node.data.name[:7], fontsize=9, ha='center', va='center', fontweight='bold', color='#2D3436')
            
            if node == bst.root:
                ax.scatter(x, y + 0.06, s=100, c='#E17055', marker='*', zorder=10)
                ax.text(x, y + 0.09, 'ROOT', fontsize=7, ha='center', va='bottom', color='#E17055', fontweight='bold')
            
            if node.left:
                lx, ly = node_info[node.left]['pos']
                ax.plot([x, lx], [y, ly], '#636E72', linewidth=2)
                ax.text((x + lx) / 2, (y + ly) / 2 + 0.01, 'L', fontsize=8, ha='center', va='bottom', color='#00B894', fontweight='bold')
                draw_tree(node.left)
            
            if node.right:
                rx, ry = node_info[node.right]['pos']
                ax.plot([x, rx], [y, ry], '#636E72', linewidth=2)
                ax.text((x + rx) / 2, (y + ry) / 2 + 0.01, 'R', fontsize=8, ha='center', va='bottom', color='#E17055', fontweight='bold')
                draw_tree(node.right)
        
        draw_tree(bst.root)
        
        total_nodes = len(node_list)
        ax.text(0.5, 0.97, f"Nodes: {total_nodes} | Height: {height}", 
                ha='center', va='center', fontsize=10, color='#636E72')
        
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#FDCB6E', edgecolor='#E67E22', label='BST Node'),
            Patch(facecolor='#00B894', label='Left Child'),
            Patch(facecolor='#E17055', label='Right Child')
        ]
        ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.08), 
                  ncol=3, fontsize=9, frameon=True, edgecolor='lightgray')
        
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.15, 1.1)
        ax.axis('off')
    
    def draw_linked_list(ax):
        ax.set_title("Recipe Ingredient Linked List (食谱食材链表)", fontsize=14, pad=20)
        
        recipe = all_recipes[0] if all_recipes else None
        if not recipe or not recipe.ingredient_list:
            ax.text(0.5, 0.5, "No recipe or empty ingredient list", 
                    ha='center', va='center', fontsize=14)
            ax.axis('off')
            return
        
        ingredients = recipe.ingredient_list.get_all_ingredients()
        n = len(ingredients)
        
        if n == 0:
            ax.text(0.5, 0.5, "Empty linked list", ha='center', va='center', fontsize=14)
            ax.axis('off')
            return
        
        margin = 0.08
        available_width = 1 - 2 * margin
        x_step = available_width / (n + 1) if n > 1 else 0
        
        node_width = 0.05
        node_height = 0.15
        y_center = 0.5
        
        for i, (ing, qty) in enumerate(ingredients):
            if n == 1:
                x = 0.5
            else:
                x = margin + (i + 1) * x_step
            
            rect_x = x - node_width / 2
            rect_y = y_center - node_height / 2
            
            rect = plt.Rectangle((rect_x, rect_y), node_width, node_height, 
                                facecolor='#74B9FF', edgecolor='#0984E3', zorder=5)
            ax.add_artist(rect)
            
            ax.text(x, y_center - 0.04, f'{ing.name[:6]}', fontsize=9, ha='center', va='center', fontweight='bold', color='white')
            ax.text(x, y_center + 0.03, f'{qty}{ing.unit}', fontsize=8, ha='center', va='center', color='#0984E3')
            
            if i < n - 1:
                if n == 1:
                    next_x = x + 0.1
                else:
                    next_x = margin + (i + 2) * x_step
                
                arrow_start = x + node_width / 2
                arrow_end = next_x - node_width / 2
                arrow_length = arrow_end - arrow_start
                
                if arrow_length > 0.02:
                    ax.arrow(arrow_start, y_center, arrow_length, 0, 
                             head_width=0.03, head_length=0.015, fc='#00B894', ec='#00B894', 
                             length_includes_head=True, linewidth=2, zorder=3)
                    ax.text(arrow_start + arrow_length / 2, y_center + 0.025, '→', fontsize=12, ha='center', va='bottom', color='#00B894')
        
        if n > 0:
            head_x = margin + x_step if n > 1 else 0.5
            ax.scatter(head_x, y_center + 0.18, s=150, c='#E17055', marker='^', zorder=10)
            ax.text(head_x, y_center + 0.23, 'HEAD', fontsize=8, ha='center', va='bottom', color='#E17055', fontweight='bold')
            
            tail_x = margin + n * x_step if n > 1 else 0.5
            ax.scatter(tail_x, y_center - 0.18, s=150, c='#FD79A8', marker='v', zorder=10)
            ax.text(tail_x, y_center - 0.23, 'TAIL', fontsize=8, ha='center', va='top', color='#FD79A8', fontweight='bold')
        
        ax.text(0.5, 0.95, f"Recipe: {recipe.name[:20]}... | Length: {n}", 
                ha='center', va='center', fontsize=10, color='#636E72')
        
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#74B9FF', edgecolor='#0984E3', label='Node'),
            Patch(facecolor='#00B894', label='Pointer'),
            Patch(facecolor='#E17055', label='Head'),
            Patch(facecolor='#FD79A8', label='Tail')
        ]
        ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.08), 
                  ncol=4, fontsize=9, frameon=True, edgecolor='lightgray')
        
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.3, 1.1)
        ax.axis('off')
    
    canvas_sg = create_visualization_container(viz_tab1, draw_supply_graph, (12, 7))
    canvas_hp = create_visualization_container(viz_tab2, draw_heap, (12, 7))
    canvas_bst = create_visualization_container(viz_tab3, draw_bst, (14, 7))
    canvas_ll = create_visualization_container(viz_tab4, draw_linked_list, (14, 6))

    # Tab10: Crisis Recovery (危机恢复)
    crisis_notebook = ttk.Notebook(tab10)
    crisis_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    crisis_tab1 = ttk.Frame(crisis_notebook)
    crisis_tab2 = ttk.Frame(crisis_notebook)
    crisis_tab3 = ttk.Frame(crisis_notebook)

    crisis_notebook.add(crisis_tab1, text="Simulate Shutdown (模拟断供)")
    crisis_notebook.add(crisis_tab2, text="Risk Assessment (风险评估)")
    crisis_notebook.add(crisis_tab3, text="Recovery Plan (恢复方案)")

    crisis_result = scrolledtext.ScrolledText(crisis_tab1, width=100, height=25)
    crisis_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    ttk.Label(crisis_tab1, text="Enter Supplier ID to simulate shutdown:").pack(side=tk.LEFT, padx=10, pady=5)
    shutdown_entry = ttk.Entry(crisis_tab1, width=10)
    shutdown_entry.pack(side=tk.LEFT, padx=5, pady=5)
    shutdown_entry.insert(0, "0")

    current_crisis = None
    original_supply_graph_state = None

    def backup_supply_graph():
        import copy
        return copy.deepcopy(supply_graph.adj), copy.deepcopy(supply_graph.ingredient_to_suppliers)

    def restore_supply_graph(adj, ingredient_to_suppliers):
        supply_graph.adj = adj
        supply_graph.ingredient_to_suppliers = ingredient_to_suppliers

    def simulate_shutdown():
        global current_crisis, original_supply_graph_state
        try:
            sid = int(shutdown_entry.get())
            if sid not in supply_graph.adj:
                messagebox.showwarning("Warning", f"Supplier ID {sid} does not exist (供应商ID{sid}不存在)")
                return

            original_supply_graph_state = backup_supply_graph()

            crisis_result.delete(1.0, tk.END)
            crisis_result.insert(tk.END, "=" * 80 + "\n")
            crisis_result.insert(tk.END, f"Simulating Supplier {sid} Shutdown (模拟供应商{sid}断供)\n")
            crisis_result.insert(tk.END, "=" * 80 + "\n\n")

            current_crisis = SupplyCrisisRecovery(supply_graph, bst, sub_graph)
            current_crisis.simulate_supplier_shutdown(sid)

            crisis_result.insert(tk.END, "Simulation completed successfully!\n")
            crisis_result.insert(tk.END, f"Supplier {sid} has been removed from the supply network.\n\n")

            crisis_result.insert(tk.END, "--- Risk Assessment Summary ---\n")
            crisis_result.insert(tk.END, f"Total recipes affected: {len(current_crisis.risk_recipes)}\n")
            crisis_result.insert(tk.END, f"Dead recipes (cannot be rescued): {len(current_crisis.dead_recipes)}\n\n")

            if current_crisis.dead_recipes:
                crisis_result.insert(tk.END, "Dead Recipes:\n")
                for r in current_crisis.dead_recipes:
                    crisis_result.insert(tk.END, f"  - {r.name}\n")

            crisis_result.insert(tk.END, "\nClick 'Generate Recovery Plan' to view detailed recovery options.\n")

        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid supplier ID")

    def reset_simulation():
        global current_crisis, original_supply_graph_state
        if original_supply_graph_state:
            restore_supply_graph(*original_supply_graph_state)
            current_crisis = None
            crisis_result.delete(1.0, tk.END)
            crisis_result.insert(tk.END, "Simulation has been reset.\n")
            crisis_result.insert(tk.END, "Supply network restored to original state.\n")
            messagebox.showinfo("Success", "Simulation reset successfully (模拟已重置)")
        else:
            messagebox.showinfo("Info", "No simulation to reset (没有可重置的模拟)")

    button_frame = ttk.Frame(crisis_tab1)
    button_frame.pack(fill=tk.X, padx=10, pady=5)
    ttk.Button(button_frame, text="Simulate Shutdown", command=simulate_shutdown).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Reset Simulation", command=reset_simulation).pack(side=tk.LEFT, padx=5)

    crisis_result.insert(tk.END, "=== Supply Chain Crisis Recovery Simulation ===\n")
    crisis_result.insert(tk.END, "-" * 80 + "\n")
    crisis_result.insert(tk.END, "Enter a supplier ID and click 'Simulate Shutdown' to test.\n")
    crisis_result.insert(tk.END, "Available supplier IDs: " + ", ".join(str(sid) for sid in supply_graph.adj.keys()) + "\n\n")
    crisis_result.insert(tk.END, "Features:\n")
    crisis_result.insert(tk.END, "  • Simulate supplier shutdown\n")
    crisis_result.insert(tk.END, "  • Risk assessment for affected recipes\n")
    crisis_result.insert(tk.END, "  • Generate recovery plan with alternative suppliers\n")

    # Tab10.2: Risk Assessment
    risk_result = scrolledtext.ScrolledText(crisis_tab2, width=100, height=25)
    risk_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def show_risk_assessment():
        risk_result.delete(1.0, tk.END)
        if not current_crisis:
            risk_result.insert(tk.END, "[error] No simulation has been run yet.\n")
            risk_result.insert(tk.END, "Please run a simulation in 'Simulate Shutdown' tab first.\n")
            return

        risk_result.insert(tk.END, "=" * 80 + "\n")
        risk_result.insert(tk.END, "Risk Assessment Report (风险评估报告)\n")
        risk_result.insert(tk.END, "=" * 80 + "\n\n")

        risk_result.insert(tk.END, f"Shutdown Supplier ID: {current_crisis.shutdown_supplier_id}\n")
        risk_result.insert(tk.END, f"Total recipes in system: {len(current_crisis.all_recipes)}\n")
        risk_result.insert(tk.END, f"Recipes affected by shutdown: {len(current_crisis.risk_recipes)}\n")
        risk_result.insert(tk.END, f"Dead recipes (cannot be rescued): {len(current_crisis.dead_recipes)}\n")
        risk_result.insert(tk.END, f"Recipes that can be rescued: {len(current_crisis.risk_recipes) - len(current_crisis.dead_recipes)}\n\n")

        risk_result.insert(tk.END, "--- Affected Recipes (受影响食谱) ---\n")
        risk_result.insert(tk.END, "-" * 60 + "\n")
        for rec, missing_ings in current_crisis.risk_recipes:
            can_rescue = "CAN RESCUE" if rec not in current_crisis.dead_recipes else "DEAD"
            risk_result.insert(tk.END, f"[{can_rescue}] {rec.name} ({rec.cuisine_type.value})\n")
            risk_result.insert(tk.END, "   Missing ingredients: ")
            for ing in missing_ings:
                risk_result.insert(tk.END, f"{ing.name} (ID:{ing.ingredient_id}) ")
            risk_result.insert(tk.END, "\n\n")

        if current_crisis.dead_recipes:
            risk_result.insert(tk.END, "\n--- Dead Recipes (致命食谱 - 无法挽救) ---\n")
            risk_result.insert(tk.END, "-" * 60 + "\n")
            for rec in current_crisis.dead_recipes:
                risk_result.insert(tk.END, f"  • {rec.name}\n")

    ttk.Button(crisis_tab2, text="Refresh Risk Assessment", command=show_risk_assessment).pack(pady=10)

    # Tab10.3: Recovery Plan
    recovery_result = scrolledtext.ScrolledText(crisis_tab3, width=100, height=25)
    recovery_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def generate_recovery_plan():
        recovery_result.delete(1.0, tk.END)
        if not current_crisis:
            recovery_result.insert(tk.END, "[error] No simulation has been run yet.\n")
            recovery_result.insert(tk.END, "Please run a simulation in 'Simulate Shutdown' tab first.\n")
            return

        recovery_result.insert(tk.END, "=" * 80 + "\n")
        recovery_result.insert(tk.END, "Supply Chain Recovery Plan (供应链恢复方案)\n")
        recovery_result.insert(tk.END, "=" * 80 + "\n\n")

        all_missing_ing_ids = set()
        for rec, missing in current_crisis.risk_recipes:
            for ing in missing:
                all_missing_ing_ids.add(ing.ingredient_id)

        recovery_result.insert(tk.END, f"Total missing ingredients: {len(all_missing_ing_ids)}\n\n")

        if len(all_missing_ing_ids) == 0:
            recovery_result.insert(tk.END, "No ingredients are missing. Recovery not needed.\n")
            return

        recovery_result.insert(tk.END, "--- Recommended Recovery Priority (按食材分组，低价优先) ---\n")
        recovery_result.insert(tk.END, "-" * 60 + "\n\n")

        recovery_list = []
        for ing_id in all_missing_ing_ids:
            suppliers = supply_graph.get_suppliers_for_ingredient(ing_id)
            supplier_cost = []
            for sid in suppliers:
                cost = supply_graph.get_unit_cost(sid, ing_id)
                supplier_cost.append((sid, cost))
            supplier_cost.sort(key=lambda x: x[1])
            recovery_list.append((ing_id, supplier_cost))

        for ing_id, sorted_supp in recovery_list:
            ing = None
            for r, miss in current_crisis.risk_recipes:
                for m in miss:
                    if m.ingredient_id == ing_id:
                        ing = m
                        break
                if ing:
                    break

            ing_name = ing.name if ing else f"ID:{ing_id}"
            recovery_result.insert(tk.END, f"Ingredient: {ing_name} (ID:{ing_id})\n")
            recovery_result.insert(tk.END, "  Recommended suppliers (lowest price first):\n")

            if sorted_supp:
                for idx, (sid, cost) in enumerate(sorted_supp, 1):
                    recovery_result.insert(tk.END, f"    {idx}. Supplier{sid} - Unit Cost: {cost:.2f}\n")
            else:
                recovery_result.insert(tk.END, "    [error] No alternative suppliers available!\n")
            recovery_result.insert(tk.END, "\n")

        recovery_result.insert(tk.END, "--- Summary ---\n")
        recovery_result.insert(tk.END, f"Total ingredients to recover: {len(all_missing_ing_ids)}\n")
        recovery_result.insert(tk.END, f"Recipes that can be rescued: {len(current_crisis.risk_recipes) - len(current_crisis.dead_recipes)}\n")
        recovery_result.insert(tk.END, f"Dead recipes: {len(current_crisis.dead_recipes)}\n")

    ttk.Button(crisis_tab3, text="Generate Recovery Plan", command=generate_recovery_plan).pack(pady=10)

    root.mainloop()
