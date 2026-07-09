# Supply Chain Optimization System (供应链优化系统)

A comprehensive software solution for catering companies to manage recipes, ingredients, suppliers, and procurement using core data structures (BST, Linked List, Graph, Heap), with advanced algorithms for substitution, optimization, and crisis recovery.

## Features (功能特性)

- **Data Structures**: BST, Linked List (with tail pointer), Weighted Graph, Max-Heap
- **Advanced Algorithms**: Ingredient substitution, supplier optimization, menu planning
- **Crisis Recovery**: Supplier shutdown simulation, risk assessment, recovery planning
- **Visualization**: Interactive GUI with 10 tabs, data structure visualization, performance charts
- **Testing**: 120+ comprehensive unit tests covering edge cases

## Project Structure (项目结构)

```
Supply_Chain_Optimizer/
├── main.py                    # Main entry point (主入口)
├── requirements.txt           # Dependencies (依赖列表)
├── README.md                  # Project documentation (项目文档)
├── data/                      # Dataset files (数据集文件)
├── reports/                   # Generated reports and charts (生成的报告和图表)
├── src/
│   ├── part1/                 # Basic Data Structures (基础数据结构)
│   │   ├── bst.py             # Binary Search Tree (二叉搜索树)
│   │   ├── linked_list.py     # Singly Linked List with Tail Pointer (单向链表)
│   │   ├── max_heap.py        # Max-Heap with Urgency Calculation (最大堆)
│   │   ├── supply_graph.py    # Supply Network Graph (供应网络图)
│   │   ├── dataset_generator.py # Dataset Generator (数据集生成器)
│   │   └── models.py          # Data Models (数据模型)
│   ├── part2/                 # Advanced Algorithms (高级算法)
│   │   ├── substitution_graph.py # Substitution Graph (食材替换图)
│   │   ├── supplier_optimizer.py # Supplier Optimizer (供应商优化器)
│   │   ├── menu_planner.py    # Weekly Menu Planner (周菜单规划器)
│   │   ├── benchmark.py       # Performance Benchmark (性能基准测试)
│   │   └── gui_app.py         # Visualization GUI (可视化GUI)
│   └── part3/                 # Crisis Recovery (危机恢复)
│       └── crisis_recovery.py # Supply Crisis Recovery (供应链危机恢复)
├── tests/
│   ├── test_part1.py          # Part1 Unit Tests (75 tests)
│   ├── test_part2.py          # Part2 Unit Tests (29 tests)
│   └── test_part3.py          # Part3 Unit Tests (16 tests)
└── .venv/                     # Virtual environment (虚拟环境)
```

## Technical Stack (技术栈)

| Category | Technology |
|----------|------------|
| Programming Language | Python 3.10+ |
| Core Concepts | Data Structures, Algorithm Design, CSV Handling, Unit Testing |
| Visualization | Tkinter GUI, Matplotlib Charts |
| Testing | unittest Framework |
| Dependencies | matplotlib>=3.7, Pillow>=9.0, numpy>=1.24 |

## Quick Start (快速开始)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main program
python main.py
```

The system automatically runs all modules in sequence:
1. **Part1**: Generate dataset, initialize data structures, run unit tests
2. **Part2**: Build substitution graph, run optimization algorithms, performance benchmark, launch GUI
3. **Part3**: Supply crisis recovery simulation

## GUI Features (可视化界面功能)

The system includes a comprehensive Tkinter GUI with **10 tabs**:

| Tab | Name | Description |
|-----|------|-------------|
| Tab1 | Recipe Search | Search recipe by name, view detailed information |
| Tab2 | Cuisine Filter | Filter recipes by cuisine type (Chinese/Western/Japanese/Thai) |
| Tab3 | Alphabet Range | Search recipes by alphabet letter range (A-F, G-M, etc.) |
| Tab4 | Ingredient Substitution | Query substitute ingredients for a given ingredient ID |
| Tab5 | Supply Network | Query suppliers for a given ingredient ID |
| Tab6 | Performance Chart | Display benchmark results with 4 sub-charts grouped by time scale |
| Tab7 | Test Results | Run all tests with detailed report and progress bar |
| Tab8 | Data Management | Add/delete recipes, ingredients, suppliers, and substitutions |
| Tab9 | Structure Visualization | Visualize data structures with zoom functionality |
| Tab10 | Crisis Recovery | Simulate supplier shutdown, assess risk, generate recovery plans |

### Tab9: Structure Visualization (结构可视化)

Contains 4 sub-tabs for visualizing core data structures:

| Sub-tab | Name | Description |
|---------|------|-------------|
| Tab9.1 | Supply Graph | Display supply network as nodes (suppliers/ingredients) and edges |
| Tab9.2 | Heap | Display procurement queue as tree structure with urgency scores |
| Tab9.3 | BST | Display recipe binary search tree with node names |
| Tab9.4 | Linked List | Display recipe ingredient linked list with nodes and arrows |

**Zoom Controls**: Each visualization supports:
- **Zoom In (+)**: 1.2x magnification
- **Zoom Out (-)**: 0.8x reduction
- **Reset**: Restore original size
- **Refresh**: Re-render the visualization
- **Scrollbars**: Navigate when zoomed in

### Tab10: Crisis Recovery (危机恢复)

Contains 3 sub-tabs for supply chain crisis management:

| Sub-tab | Name | Description |
|---------|------|-------------|
| Tab10.1 | Simulate Shutdown | Input supplier ID to simulate shutdown, view risk summary |
| Tab10.2 | Risk Assessment | Detailed report of affected recipes, distinguish rescuable vs dead recipes |
| Tab10.3 | Recovery Plan | Generate recovery priority list with alternative suppliers (sorted by cost) |

### Tab6: Performance Chart (性能图表)

The performance benchmark chart shows algorithm scalability across different input sizes (20-2000 recipes):

| Sub-chart | Operations | Time Scale |
|-----------|------------|------------|
| Top-Left | BST Search, Graph Search, Linked List Iter | Nanoseconds (ns) |
| Top-Right | BST Insert, Supplier Optimization | Microseconds (μs) |
| Bottom-Left | Heap Top-10, BST In-order | Milliseconds (ms) |
| Bottom-Right | All Recipe Feasibility Check | Milliseconds (ms) |

**Features**:
- Logarithmic Y-axis to display multiple orders of magnitude
- Data point annotations with scientific notation
- Independent Y-axis ranges for each sub-chart
- Generated automatically and saved to `./reports/benchmark_plot.png`

## Core Data Structures (核心数据结构)

### Binary Search Tree (BST) - Recipe Catalogue
- **Key**: Recipe name (case-insensitive alphabetical order)
- **Operations**: Insert, delete, search, cuisine filter, range search, get feasible recipes
- **Complexity**: O(log n) average, O(n) worst

### Singly Linked List with Tail Pointer - Recipe Ingredients
- **Structure**: Stores (Ingredient, quantity) pairs
- **Operations**: Add (O(1) with tail), remove, update, check feasibility
- **Complexity**: O(1) insert/append, O(n) search/remove

### Weighted Directed Graph - Supply Network
- **Nodes**: Suppliers
- **Edges**: Supply relationships with unit cost weights
- **Operations**: Add/remove suppliers, find suppliers for ingredient, get cheapest supplier

### Max-Heap - Procurement Priority
- **Key**: Urgency score
- **Urgency Formula**: `shortage × 10 + depend_count + (30 - lead_time)`
- **Operations**: Push, pop highest, get top-K

## Advanced Algorithms (高级算法)

### Substitution Graph (食材替换图)
- Build substitution relationships between ingredients
- Find all substitutes sorted by quality score
- Check recipe feasibility with substitutions

### Supplier Optimizer (供应商优化器)
- Find minimum cost supplier combination for recipes
- Filter suppliers by reliability threshold

### Weekly Menu Planner (周菜单规划器)
- Analyze weekly menu feasibility
- Identify ingredient shortages
- Generate procurement plans

### Supply Crisis Recovery (供应链危机恢复)
- Simulate supplier shutdown scenarios
- Scan and classify risk recipes
- Generate recovery plans with alternative suppliers

## Testing Coverage (测试覆盖)

### Part1 Tests (75 tests)
- **BST**: Insert, search (case-sensitive/insensitive), delete, range search, cuisine filter, height calculation
- **Linked List**: Add, remove, update quantity, edge cases (empty, None, negative IDs)
- **Max-Heap**: Push, pop, get top-K, edge cases (empty, duplicates)
- **Supply Graph**: Add/remove suppliers, get suppliers, get cheapest, unit cost
- **Integration Tests**: BST in-order, linked list length match, heap highest urgency

### Part2 Tests (29 tests)
- **Substitution Graph**: Register ingredients, add substitutions, get substitutes, rank options
- **Supplier Optimizer**: Add suppliers, get minimum cost combinations, reliability filtering
- **Weekly Menu Planner**: Analyze menu, generate procurement plans
- **Performance Benchmark**: Scalability testing from 20 to 2000 recipes

### Part3 Tests (16 tests)
- **Supply Crisis Recovery**: Simulate shutdown, scan risk recipes, generate recovery plans, edge cases

## Performance Characteristics (性能特征)

| Data Structure | Insert | Search | Delete |
|----------------|--------|--------|--------|
| BST | O(log n) avg, O(n) worst | O(log n) avg, O(n) worst | O(log n) avg, O(n) worst |
| Linked List (with tail) | O(1) | O(n) | O(n) |
| Supply Graph | O(1) | O(\|V\|+\|E\|) | O(1) |
| Max-Heap | O(log n) | O(1) for max | O(log n) |

## Data Models (数据模型)

| Entity | Key Attributes |
|--------|----------------|
| **Ingredient** | ingredient_id, name, category, unit, current_stock, minimum_stock, lead_time |
| **Recipe** | recipe_id, name, cuisine_type, difficulty, prep_time_minutes, servings, ingredient_list |
| **Supplier** | supplier_id, name, location, reliability_score |

## Core Technical Decisions (核心技术决策)

### BST vs Python List for Search
- **BST**: O(log n) average search time
- **List**: O(n) search time
- **Justification**: For 10,000 recipes, BST requires ~14 comparisons vs ~5,000 for a list

### Linked List with Tail Pointer
- **Benefits**: O(1) insertion at end, no pre-allocation, dynamic memory
- **Use Case**: Recipe ingredients change frequently

### Urgency Score Formula
- `shortage × 10`: Stock deficit is most critical (halts production)
- `depend_count`: Number of recipes affected
- `(30 - lead_time)`: Shorter lead time = faster restocking = lower urgency

## License
This project is for educational purposes.
