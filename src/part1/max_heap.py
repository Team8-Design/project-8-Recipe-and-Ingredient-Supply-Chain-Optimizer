from src.part1.models import Ingredient

class UrgencyMaxHeap:
    def __init__(self):
        self.heap = []
        self.ing_map = dict()  # ingredient_id -> heap index

    @staticmethod
    def calc_urgency_score(ing: Ingredient, depend_count: int) -> float:
        """自定义紧急度公式：缺口*10 + 依赖食谱数 + (30-交货期)"""
        shortage = ing.stock_shortage()
        score = shortage * 10 + depend_count + (30 - ing.lead_time)
        return round(score, 2)

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.ing_map[self.heap[i][1].ingredient_id] = i
        self.ing_map[self.heap[j][1].ingredient_id] = j

    def _heapify_up(self, idx):
        parent = (idx - 1) // 2
        while idx > 0 and self.heap[idx][0] > self.heap[parent][0]:
            self._swap(idx, parent)
            idx = parent
            parent = (idx - 1) // 2

    def _heapify_down(self, idx):
        size = len(self.heap)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            largest = idx
            if left < size and self.heap[left][0] > self.heap[largest][0]:
                largest = left
            if right < size and self.heap[right][0] > self.heap[largest][0]:
                largest = right
            if largest == idx:
                break
            self._swap(idx, largest)
            idx = largest

    def push(self, ing: Ingredient, depend_count: int):
        score = self.calc_urgency_score(ing, depend_count)
        entry = (score, ing)
        if ing.ingredient_id in self.ing_map:
            # 更新已有食材紧急度
            pos = self.ing_map[ing.ingredient_id]
            self.heap[pos] = entry
            self._heapify_up(pos)
            return
        self.heap.append(entry)
        self.ing_map[ing.ingredient_id] = len(self.heap) - 1
        self._heapify_up(len(self.heap)-1)

    def pop_highest(self) -> tuple[float, Ingredient] | None:
        if not self.heap:
            return None
        top = self.heap[0]
        del self.ing_map[top[1].ingredient_id]
        if len(self.heap) == 1:
            self.heap.clear()
            return top
        last = self.heap.pop()
        self.heap[0] = last
        self.ing_map[last[1].ingredient_id] = 0
        self._heapify_down(0)
        return top

    def get_top_k(self, k: int) -> list[tuple[float, Ingredient]]:
        temp = []
        res = []
        for _ in range(min(k, len(self.heap))):
            item = self.pop_highest()
            res.append(item)
            temp.append(item)
        # 放回堆
        for s, ing in temp:
            self.push(ing, 0)
        return res

    def size(self):
        return len(self.heap)