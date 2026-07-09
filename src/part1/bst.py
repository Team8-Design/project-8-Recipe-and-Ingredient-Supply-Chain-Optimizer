from src.part1.models import Recipe, CuisineType
from src.part1.linked_list import RecipeIngredientLinkedList  # 引入链表类做类型提示


class BSTNode:
    def __init__(self, recipe: Recipe):
        self.data = recipe
        self.left = None
        self.right = None


class RecipeBST:
    def __init__(self):
        self.root = None

    def insert(self, recipe: Recipe):
        """插入食谱（按名称字典序，同名食谱存入右子树）"""
        if recipe is None:
            raise TypeError("Recipe cannot be None")
        new_node = BSTNode(recipe)
        if self.root is None:
            self.root = new_node
            return

        curr = self.root
        while True:
            # 严格按名称字典序比较（忽略大小写，避免大小写不一致问题）
            recipe_name_lower = recipe.name.lower()
            curr_name_lower = curr.data.name.lower()

            if recipe_name_lower < curr_name_lower:
                if curr.left is None:
                    curr.left = new_node
                    break
                curr = curr.left
            else:
                if curr.right is None:
                    curr.right = new_node
                    break
                curr = curr.right

    def search(self, recipe_name: str, case_sensitive: bool = False) -> Recipe | None:
        """
        搜索指定名称的食谱
        :param recipe_name: 食谱名称
        :param case_sensitive: 是否区分大小写（默认不区分）
        :return: 匹配的Recipe对象，无则返回None
        """
        curr = self.root
        target_name = recipe_name if case_sensitive else recipe_name.lower()

        while curr:
            curr_name = curr.data.name if case_sensitive else curr.data.name.lower()
            if curr_name == target_name:
                return curr.data
            elif target_name < curr_name:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def in_order(self, iterative: bool = True) -> list[Recipe]:
        """
        中序遍历（迭代实现，避免栈溢出；可选递归兼容旧逻辑）
        :param iterative: 是否使用迭代方式（默认是）
        :return: 按名称升序排列的食谱列表
        """
        res = []
        if not self.root:
            return res

        if iterative:
            # 迭代式中序遍历（推荐）
            stack = []
            curr = self.root
            while stack or curr:
                while curr:
                    stack.append(curr)
                    curr = curr.left
                curr = stack.pop()
                res.append(curr.data)
                curr = curr.right
        else:
            # 递归式中序遍历（兼容旧代码）
            def traverse(node):
                if node:
                    traverse(node.left)
                    res.append(node.data)
                    traverse(node.right)

            traverse(self.root)
        return res

    def get_recipes_by_cuisine(self, target_cuisine: CuisineType) -> list[Recipe]:
        """按菜系筛选食谱（遍历BST时直接筛选，优化效率）"""
        matches = []
        stack = []
        curr = self.root

        # 迭代遍历+BST筛选，无需全量生成列表后再过滤
        while stack or curr:
            while curr:
                stack.append(curr)
                curr = curr.left
            curr = stack.pop()
            if curr.data.cuisine_type == target_cuisine:
                matches.append(curr.data)
            curr = curr.right
        return matches

    def range_search(self, start_letter: str, end_letter: str, case_sensitive: bool = False) -> list[Recipe]:
        """
        按名称首字母范围搜索（A-F, a-f 等）
        :param start_letter: 起始字母（单字符）
        :param end_letter: 结束字母（单字符）
        :param case_sensitive: 是否区分大小写
        :return: 首字母在[start, end]范围内的食谱列表
        """
        matches = []
        if not self.root or len(start_letter) != 1 or len(end_letter) != 1:
            return matches

        # 统一大小写（避免大小写问题）
        start = start_letter if case_sensitive else start_letter.upper()
        end = end_letter if case_sensitive else end_letter.upper()

        stack = []
        curr = self.root
        while stack or curr:
            while curr:
                stack.append(curr)
                curr = curr.left
            curr = stack.pop()
            # 取名称首字符并统一大小写
            first_char = curr.data.name[0] if case_sensitive else curr.data.name[0].upper()
            if start <= first_char <= end:
                matches.append(curr.data)
            curr = curr.right
        return matches

    def get_all_feasible_recipes(self) -> list[Recipe]:
        """筛选所有库存可行的食谱（修复方法名错误+遍历优化）"""
        feasible = []
        stack = []
        curr = self.root

        while stack or curr:
            while curr:
                stack.append(curr)
                curr = curr.left
            curr = stack.pop()
            # 修复：调用正确的方法名 check_recipe_feasible
            is_feasible, _ = curr.data.ingredient_list.check_recipe_feasible()
            if is_feasible:
                feasible.append(curr.data)
            curr = curr.right
        return feasible

    def delete(self, recipe_name: str, case_sensitive: bool = False) -> bool:
        """
        删除指定名称的食谱（BST节点删除逻辑）
        :return: 是否删除成功
        """
        if not self.root:
            return False

        # 辅助函数：找右子树最小节点（删除节点的替代节点）
        def find_min_node(node: BSTNode) -> BSTNode:
            current = node
            while current.left:
                current = current.left
            return current

        # 递归删除核心逻辑
        def _delete(node: BSTNode, target: str) -> tuple[BSTNode | None, bool]:
            if not node:
                return None, False

            target_lower = target if case_sensitive else target.lower()
            node_name_lower = node.data.name if case_sensitive else node.data.name.lower()

            if target_lower < node_name_lower:
                node.left, deleted = _delete(node.left, target)
            elif target_lower > node_name_lower:
                node.right, deleted = _delete(node.right, target)
            else:
                # 找到要删除的节点
                deleted = True
                # 情况1：叶子节点 或 只有一个子节点
                if not node.left:
                    return node.right, deleted
                elif not node.right:
                    return node.left, deleted
                # 情况2：有两个子节点 → 用右子树最小节点替代
                min_right = find_min_node(node.right)
                node.data = min_right.data
                # 删除右子树最小节点
                node.right, _ = _delete(node.right, min_right.data.name)
            return node, deleted

        self.root, deleted = _delete(self.root, recipe_name)
        return deleted

    def get_bst_height(self) -> int:
        """计算BST高度（用于检测是否失衡）"""

        def _height(node: BSTNode) -> int:
            if not node:
                return 0
            left_h = _height(node.left)
            right_h = _height(node.right)
            return max(left_h, right_h) + 1

        return _height(self.root)

    def get_height(self) -> int:
        return self.get_bst_height()