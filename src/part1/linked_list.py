from src.part1.models import Ingredient

class ListNode:
    def __init__(self, ingredient: Ingredient, quantity: float):
        self.ingredient = ingredient
        self.quantity = quantity
        self.next = None

class RecipeIngredientLinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def add_ingredient(self, ing: Ingredient, qty: float):
        new_node = ListNode(ing, qty)
        if not self.head:
            self.head = new_node
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = new_node
        self.size += 1

    def remove_ingredient(self, ing_id: int):
        if not self.head:
            return False
        if self.head.ingredient.ingredient_id == ing_id:
            self.head = self.head.next
            self.size -= 1
            return True
        cur = self.head
        while cur.next:
            if cur.next.ingredient.ingredient_id == ing_id:
                cur.next = cur.next.next
                self.size -= 1
                return True
            cur = cur.next
        return False

    def update_quantity(self, ing_id: int, new_qty: float):
        cur = self.head
        while cur:
            if cur.ingredient.ingredient_id == ing_id:
                cur.quantity = new_qty
                return True
            cur = cur.next
        return False

    def calculate_total_cost(self, supply_graph):
        """遍历链表，结合供应图计算食谱总采购成本"""
        total = 0.0
        cur = self.head
        while cur:
            ing = cur.ingredient
            qty = cur.quantity
            suppliers = supply_graph.get_suppliers_for_ingredient(ing.ingredient_id)
            if suppliers:
                cheapest_cost = min([supply_graph.get_unit_cost(sid, ing.ingredient_id) for sid in suppliers])
                total += cheapest_cost * qty
            cur = cur.next
        return round(total, 2)

    def check_recipe_feasible(self) -> tuple[bool, list]:
        """校验当前库存能否制作，返回(是否可行, 短缺食材列表)"""
        shortage = []
        cur = self.head
        while cur:
            ing = cur.ingredient
            if ing.current_stock < cur.quantity:
                shortage.append(ing)
            cur = cur.next
        return len(shortage) == 0, shortage

    def get_all_ingredients(self):
        res = []
        cur = self.head
        while cur:
            res.append((cur.ingredient, cur.quantity))
            cur = cur.next
        return res