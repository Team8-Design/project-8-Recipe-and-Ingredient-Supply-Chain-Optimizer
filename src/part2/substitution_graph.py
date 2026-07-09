from src.part1.models import Ingredient

class SubstitutionGraph:
    def __init__(self):
        # key: ingredient_id, value: list[(target_ing_id, quality_score)]
        self.sub_edges = {}
        self.ingredient_map = {}

    def register_ingredient(self, ing: Ingredient):
        self.ingredient_map[ing.ingredient_id] = ing
        if ing.ingredient_id not in self.sub_edges:
            self.sub_edges[ing.ingredient_id] = []

    def add_substitution_pair(self, ing1_id: int, ing2_id: int, quality: float):
        """添加无向替换边，quality 0~1"""
        assert 0.0 <= quality <= 1.0
        if ing1_id not in self.sub_edges:
            self.sub_edges[ing1_id] = []
        if ing2_id not in self.sub_edges:
            self.sub_edges[ing2_id] = []
        self.sub_edges[ing1_id].append((ing2_id, quality))
        self.sub_edges[ing2_id].append((ing1_id, quality))

    def build_default_substitution(self):
        """预置默认食材替换关系"""
        pairs = [
            (4, 13, 0.9),  # milk <-> coconut_milk
            (5, 12, 0.85), # butter <-> cream
            (1, 3, 0.6),   # beef <-> pork
            (6, 14, 0.75), # flour <-> noodle
            (15, 1, 0.65)  # shrimp <-> beef
        ]
        for i1, i2, q in pairs:
            self.add_substitution_pair(i1, i2, q)

    def get_all_substitutes(self, missing_ing_id: int) -> list[tuple[Ingredient, float]]:
        """获取某食材所有可替代食材，按质量分降序"""
        if missing_ing_id not in self.sub_edges:
            return []
        res = []
        for target_id, score in self.sub_edges[missing_ing_id]:
            if target_id in self.ingredient_map:
                res.append((self.ingredient_map[target_id], score))
        # 降序排序
        res.sort(key=lambda x: x[1], reverse=True)
        return res

    def check_recipe_with_substitute(self, recipe, missing_ing: Ingredient, substitute_ing: Ingredient, need_qty: float):
        """替换后判断食谱是否可制作：替换食材库存 >= 需要量"""
        return substitute_ing.current_stock >= need_qty

    def rank_substitution_options(self, recipe, missing_ing: Ingredient, needed_qty: float):
        """生成排序后的替换方案列表"""
        subs = self.get_all_substitutes(missing_ing.ingredient_id)
        result = []
        for sub_ing, quality in subs:
            feasible = self.check_recipe_with_substitute(recipe, missing_ing, sub_ing, needed_qty)
            result.append({
                "substitute_ingredient": sub_ing,
                "quality_score": quality,
                "can_make": feasible
            })
        return sorted(result, key=lambda x: x["quality_score"], reverse=True)