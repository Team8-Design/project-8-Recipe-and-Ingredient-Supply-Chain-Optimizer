import time
import tempfile
import shutil
import matplotlib.pyplot as plt
from src.part1.dataset_generator import DatasetGenerator
from src.part1.bst import RecipeBST
from src.part1.max_heap import UrgencyMaxHeap
from src.part1.supply_graph import SupplyGraph

plt.rcParams["font.sans-serif"] = ["SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "dejavusans"

class BenchmarkTester:
    def __init__(self):
        self.scales = [20, 50, 100, 200, 500, 1000, 2000]
        self.results = {
            "bst_search": [],
            "all_recipe_feasibility": [],
            "supplier_opt": [],
            "heap_top10": [],
            "bst_insert": [],
            "bst_in_order": [],
            "graph_search": [],
            "linked_list_iter": []
        }
        self.temp_dir = tempfile.mkdtemp()

    def __del__(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def generate_scale_data(self, n):
        gen = DatasetGenerator(data_dir=self.temp_dir)
        gen.generate_ingredients(n)
        gen.generate_suppliers(6)
        gen.generate_recipes(n)
        gen.generate_supply_relationships(n*2)
        gen.write_csv()
        bst, sg, heap, rmap, _ = gen.load_all_data()
        return bst, sg, heap, rmap, gen

    def run_single_test(self, n):
        bst, sg, heap, rmap, gen = self.generate_scale_data(n)
        sample_recipe = list(rmap.values())[0]
        sample_ing = gen.ingredients[0]

        # 1.BST搜索耗时 - 增加迭代次数
        start = time.time()
        for _ in range(10000):
            bst.search(sample_recipe.name)
        t1 = (time.time() - start) / 10000

        # 2.全部食谱可行性校验
        start = time.time()
        for _ in range(10):
            bst.get_all_feasible_recipes()
        t2 = (time.time() - start) / 10

        # 3.最优供应商计算
        from src.part2.supplier_optimizer import SupplierOptimizer
        opt = SupplierOptimizer(sg)
        start = time.time()
        for _ in range(100):
            opt.get_min_cost_supplier_set(sample_recipe, 0.6)
        t3 = (time.time() - start) / 100

        # 4.堆提取top10 - 增加迭代次数
        start = time.time()
        for _ in range(10000):
            heap.get_top_k(10)
        t4 = (time.time() - start) / 10000

        # 5.BST插入 - 增加迭代次数
        start = time.time()
        for i in range(500):
            from src.part1.models import Recipe, CuisineType, Difficulty
            new_recipe = Recipe(9999 + i, f"Test{i}", CuisineType.CHINESE, Difficulty.EASY, 30, 4)
            bst.insert(new_recipe)
        t5 = (time.time() - start) / 500

        # 6.BST中序遍历（多次执行取平均值）
        start = time.time()
        for _ in range(100):
            bst.in_order()
        t6 = (time.time() - start) / 100

        # 7.供应图搜索供应商 - 增加迭代次数
        start = time.time()
        for _ in range(10000):
            sg.get_suppliers_for_ingredient(sample_ing.ingredient_id)
        t7 = (time.time() - start) / 10000

        # 8.链表遍历 - 增加迭代次数
        start = time.time()
        for _ in range(10000):
            sample_recipe.ingredient_list.get_all_ingredients()
        t8 = (time.time() - start) / 10000

        self.results["bst_search"].append(t1)
        self.results["all_recipe_feasibility"].append(t2)
        self.results["supplier_opt"].append(t3)
        self.results["heap_top10"].append(t4)
        self.results["bst_insert"].append(t5)
        self.results["bst_in_order"].append(t6)
        self.results["graph_search"].append(t7)
        self.results["linked_list_iter"].append(t8)

    def run_benchmark(self):
        print("Starting performance benchmark (开始性能基准测试), scales: 20/50/100/200/500/1000/2000")
        for size in self.scales:
            self.run_single_test(size)
            print(f"Completed scale {size} test (完成规模{size}测试)")
        self.plot_chart()

    def plot_chart(self):
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        def plot_with_labels(ax, x, y_list, labels, title, xlabel, ylabel, use_log=True):
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
            markers = ['o', 's', '^', 'D', 'v']
            
            all_y_values = []
            for i, (y, label) in enumerate(zip(y_list, labels)):
                positive_y = [val if val > 0 else 1e-20 for val in y]
                ax.plot(x, positive_y, marker=markers[i % len(markers)], label=label, color=colors[i % len(colors)], 
                        linewidth=2, markersize=8)
                all_y_values.extend([val for val in y if val > 0])
                for xi, yi in zip(x, y):
                    if yi > 0:
                        ax.annotate(f'{yi:.2e}', (xi, yi), textcoords="offset points", xytext=(0,8), 
                                    ha='center', fontsize=6, color=colors[i % len(colors)], fontweight='bold')
            
            ax.set_xlabel(xlabel, fontsize=11)
            ax.set_ylabel(ylabel, fontsize=11)
            ax.set_title(title, fontsize=13, fontweight='bold', pad=12)
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3, linestyle='--')
            
            if len(all_y_values) > 0:
                y_min = min(all_y_values) * 0.1 if min(all_y_values) > 0 else 1e-20
                y_max = max(all_y_values) * 10
                
                if use_log:
                    ax.set_yscale('log')
                else:
                    ax.set_ylim(y_min, y_max)

        plot_with_labels(
            axes[0, 0],
            self.scales,
            [self.results["bst_search"], self.results["graph_search"], self.results["linked_list_iter"]],
            ["BST Search", "Graph Search", "Linked List Iter"],
            "Fast Operations (ns scale) - 快速操作",
            "Recipe Count N",
            "Time (seconds)",
            use_log=True
        )

        plot_with_labels(
            axes[0, 1],
            self.scales,
            [self.results["bst_insert"], self.results["supplier_opt"]],
            ["BST Insert", "Supplier Opt"],
            "Medium Operations (μs scale) - 中等操作",
            "Recipe Count N",
            "Time (seconds)",
            use_log=True
        )

        plot_with_labels(
            axes[1, 0],
            self.scales,
            [self.results["heap_top10"], self.results["bst_in_order"]],
            ["Heap Top-10", "BST In-order"],
            "Slow Operations (ms scale) - 较慢操作",
            "Recipe Count N",
            "Time (seconds)",
            use_log=True
        )

        plot_with_labels(
            axes[1, 1],
            self.scales,
            [self.results["all_recipe_feasibility"]],
            ["All Recipe Feasibility"],
            "Feasibility Check - 可行性检查",
            "Recipe Count N",
            "Time (seconds)",
            use_log=True
        )

        plt.tight_layout()
        plt.savefig("./reports/benchmark_plot.png", dpi=300)
        plt.close()
        print("Performance chart saved to ./reports/benchmark_plot.png")
