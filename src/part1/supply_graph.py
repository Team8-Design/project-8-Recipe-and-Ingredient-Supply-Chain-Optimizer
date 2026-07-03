class SupplyGraph:
    def __init__(self):
        # adj: key=supplier_id, value={ingredient_id: unit_cost}
        self.adj = dict()
        # 反向映射：ingredient_id -> list[supplier_id]
        self.ingredient_to_suppliers = dict()

    def add_supplier(self, supplier_id: int):
        if supplier_id not in self.adj:
            self.adj[supplier_id] = {}

    def remove_supplier(self, supplier_id: int):
        if supplier_id not in self.adj:
            return
        # 删除供应商所有供应关系
        ing_ids = list(self.adj[supplier_id].keys())
        for ing_id in ing_ids:
            self.ingredient_to_suppliers[ing_id].remove(supplier_id)
            if len(self.ingredient_to_suppliers[ing_id]) == 0:
                del self.ingredient_to_suppliers[ing_id]
        del self.adj[supplier_id]

    def add_supply_relation(self, supplier_id: int, ingredient_id: int, cost_per_unit: float):
        self.add_supplier(supplier_id)
        self.adj[supplier_id][ingredient_id] = cost_per_unit
        if ingredient_id not in self.ingredient_to_suppliers:
            self.ingredient_to_suppliers[ingredient_id] = []
        if supplier_id not in self.ingredient_to_suppliers[ingredient_id]:
            self.ingredient_to_suppliers[ingredient_id].append(supplier_id)

    def remove_supply_relation(self, supplier_id: int, ingredient_id: int):
        if supplier_id in self.adj and ingredient_id in self.adj[supplier_id]:
            del self.adj[supplier_id][ingredient_id]
            self.ingredient_to_suppliers[ingredient_id].remove(supplier_id)
            if len(self.ingredient_to_suppliers[ingredient_id]) == 0:
                del self.ingredient_to_suppliers[ingredient_id]

    def get_suppliers_for_ingredient(self, ing_id: int) -> list[int]:
        return self.ingredient_to_suppliers.get(ing_id, [])

    def get_unit_cost(self, sid: int, ing_id: int) -> float:
        return self.adj[sid][ing_id]

    def get_cheapest_supplier(self, ing_id: int) -> tuple[int, float] | None:
        suppliers = self.get_suppliers_for_ingredient(ing_id)
        if not suppliers:
            return None
        min_cost = float("inf")
        best_sid = -1
        for sid in suppliers:
            c = self.get_unit_cost(sid, ing_id)
            if c < min_cost:
                min_cost = c
                best_sid = sid
        return best_sid, min_cost

    def get_ingredients_under_budget(self, budget: float) -> list[int]:
        """筛选单位成本低于预算的食材ID"""
        res = set()
        for sid in self.adj:
            for ing_id, cost in self.adj[sid].items():
                if cost <= budget:
                    res.add(ing_id)
        return list(res)