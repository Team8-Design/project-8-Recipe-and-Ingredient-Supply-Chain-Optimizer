from src.part1.supply_graph import SupplyGraph
from src.part1.models import Recipe, Supplier

class SupplierOptimizer:
    def __init__(self, supply_graph: SupplyGraph):
        self.graph = supply_graph
        self.supplier_map = {}

    def add_supplier(self, supplier: Supplier):
        self.supplier_map[supplier.supplier_id] = supplier

    def get_min_cost_supplier_set(self, recipe: Recipe, reliability_threshold: float):
        """
        给定食谱，筛选可靠性达标供应商，求最小总采购成本组合
        返回 (供应商字典{ing_id:sid}, 总成本)
        """
        total_cost = 0.0
        supplier_selection = {}
        ing_list = recipe.ingredient_list.get_all_ingredients()

        for ing, qty in ing_list:
            ing_id = ing.ingredient_id
            all_sids = self.graph.get_suppliers_for_ingredient(ing_id)
            valid_suppliers = []
            for sid in all_sids:
                if sid in self.supplier_map:
                    supplier = self.supplier_map[sid]
                    if supplier.reliability_score >= reliability_threshold:
                        unit_cost = self.graph.get_unit_cost(sid, ing_id)
                        valid_suppliers.append((sid, unit_cost))
                else:
                    unit_cost = self.graph.get_unit_cost(sid, ing_id)
                    valid_suppliers.append((sid, unit_cost))
            if not valid_suppliers:
                return None, float("inf")
            valid_suppliers.sort(key=lambda x: x[1])
            best_sid, best_unit = valid_suppliers[0]
            supplier_selection[ing_id] = best_sid
            total_cost += best_unit * qty
        return supplier_selection, round(total_cost, 2)