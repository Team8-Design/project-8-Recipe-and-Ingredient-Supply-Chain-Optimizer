from src.part1.models import Recipe, CuisineType

class BSTNode:
    def __init__(self, recipe: Recipe):
        self.recipe = recipe
        self.left = None
        self.right = None

class RecipeBST:
    def __init__(self):
        self.root = None

    def insert(self, recipe: Recipe):
        """按食谱名称字母序插入BST"""
        def _insert(node, rec):
            if not node:
                return BSTNode(rec)
            if rec.name.lower() < node.recipe.name.lower():
                node.left = _insert(node.left, rec)
            else:
                node.right = _insert(node.right, rec)
            return node
        self.root = _insert(self.root, recipe)

    def search_by_name(self, name: str) -> Recipe | None:
        """根据食谱名称精确搜索"""
        def _search(node, target):
            if not node:
                return None
            if node.recipe.name.lower() == target.lower():
                return node.recipe
            if target.lower() < node.recipe.name.lower():
                return _search(node.left, target)
            else:
                return _search(node.right, target)
        return _search(self.root, name)

    def find_by_cuisine(self, cuisine: CuisineType) -> list[Recipe]:
        """筛选指定菜系所有食谱"""
        res = []
        def traverse(node):
            if not node:
                return
            if node.recipe.cuisine_type == cuisine:
                res.append(node.recipe)
            traverse(node.left)
            traverse(node.right)
        traverse(self.root)
        return res

    def range_search(self, start_char: str, end_char: str) -> list[Recipe]:
        """区间搜索：名称首字母在start-end之间"""
        res = []
        s = start_char.lower()
        e = end_char.lower()
        def traverse(node):
            if not node:
                return
            first = node.recipe.name[0].lower()
            if s <= first <= e:
                res.append(node.recipe)
            traverse(node.left)
            traverse(node.right)
        traverse(self.root)
        return res

    def get_all_feasible_recipes(self) -> list[Recipe]:
        """遍历所有食谱，筛选当前库存可制作的食谱"""
        feasible = []
        def traverse(node):
            if not node:
                return
            ok, _ = node.recipe.ingredient_list.check_recipe_feasible()
            if ok:
                feasible.append(node.recipe)
            traverse(node.left)
            traverse(node.right)
        traverse(self.root)
        return feasible

    def in_order(self) -> list[Recipe]:
        """中序遍历，返回字母排序的食谱列表"""
        lst = []
        def mid(node):
            if not node:
                return
            mid(node.left)
            lst.append(node.recipe)
            mid(node.right)
        mid(self.root)
        return lst