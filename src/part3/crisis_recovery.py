from src.part1.supply_graph import SupplyGraph
from src.part1.bst import RecipeBST
from src.part2.substitution_graph import SubstitutionGraph

class SupplyCrisisRecovery:
    def __init__(self, supply_graph: SupplyGraph, bst: RecipeBST, sub_graph: SubstitutionGraph):
        self.graph = supply_graph
        self.bst = bst
        self.sub_graph = sub_graph
        self.all_recipes = self.bst.in_order()
        self.risk_recipes = []          # 断供后受影响食谱
        self.dead_recipes = []          # 无法替换挽救的致命食谱
        self.shutdown_supplier_id = None

    def simulate_supplier_shutdown(self, supplier_id: int):
        """模拟供应商彻底断供，从供应图移除"""
        self.shutdown_supplier_id = supplier_id
        self.graph.remove_supplier(supplier_id)
        print(f"=== Supplier {supplier_id} shutdown (供应商{supplier_id}已断供), starting risk assessment (开始风险评估) ===")
        self._scan_risk_recipes()

    def _scan_risk_recipes(self):
        """遍历所有食谱，标记受影响、无法挽救的菜品"""
        self.risk_recipes.clear()
        self.dead_recipes.clear()
        for rec in self.all_recipes:
            feasible, missing_ings = rec.ingredient_list.check_recipe_feasible()
            if feasible:
                continue
            self.risk_recipes.append((rec, missing_ings))
            # 判断是否存在可替换食材
            can_rescue = False
            for miss_ing in missing_ings:
                substitutes = self.sub_graph.get_all_substitutes(miss_ing.ingredient_id)
                if len(substitutes) > 0:
                    can_rescue = True
                    break
            if not can_rescue:
                self.dead_recipes.append(rec)

    def report_risk_recipes(self):
        """打印风险报告"""
        print(f"\n1. Total recipes affected by shutdown (受断供影响食谱总数): {len(self.risk_recipes)}")
        print(f"2. Dead recipes that cannot be rescued by substitution (无法通过食材替换挽救的致命食谱): {len(self.dead_recipes)}")
        for r in self.dead_recipes:
            print(f"   - {r.name}")

    def generate_recovery_plan(self):
        """生成最低成本、最高覆盖的替代供应商恢复方案"""
        print("\n===== Supply Chain Recovery Procurement Plan (供应链恢复采购方案) =====")
        # 收集所有短缺食材
        all_missing_ing_ids = set()
        for rec, missing in self.risk_recipes:
            for ing in missing:
                all_missing_ing_ids.add(ing.ingredient_id)
        # 按食材遍历可用供应商，按单价升序
        recovery_list = []
        for ing_id in all_missing_ing_ids:
            suppliers = self.graph.get_suppliers_for_ingredient(ing_id)
            supplier_cost = []
            for sid in suppliers:
                cost = self.graph.get_unit_cost(sid, ing_id)
                supplier_cost.append((sid, cost))
            supplier_cost.sort(key=lambda x: x[1])
            recovery_list.append((ing_id, supplier_cost))
        # 输出恢复优先级
        for ing_id, sorted_supp in recovery_list:
            print(f"Ingredient ID {ing_id} recommended supplier order (食材ID{ing_id}推荐联系供应商顺序) (lowest price first - 低价优先):")
            for sid, cost in sorted_supp:
                print(f"   Supplier{sid} (供应商{sid}) unit cost (单位成本): {cost}")