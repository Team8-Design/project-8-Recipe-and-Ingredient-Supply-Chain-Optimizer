# Supply Chain Optimization System (供应链优化系统)

A comprehensive software solution for catering companies to manage recipes, ingredients, suppliers, and procurement using core data structures (BST, Linked List, Graph, Heap).

## Project Overview (项目概述)

This system is designed to address the key operational needs of a catering company:
- Organize recipe catalogs for efficient searching (高效搜索食谱目录)
- Optimize ingredient sourcing (cheapest/nearest/most reliable supplier) (优化食材采购)
- Detect possible ingredient substitutions (检测食材替代方案)
- Manage weekly procurement priority lists (管理每周采购优先级列表)
- Leverage four fundamental data structures with distinct roles in the system architecture (利用四种基础数据结构解决不同业务问题)

## System Architecture & Core Components (系统架构与核心组件)

### 1. Data Models (数据模型)

The system is built around three core entities with well-defined attributes:

| Entity | Key Attributes |
|--------|----------------|
| **Ingredient (食材)** | ingredient_id, name, category (PRODUCE/DAIRY/MEAT/GRAIN/SPICE), unit, current_stock, minimum_stock |
| **Recipe (食谱)** | recipe_id, name, cuisine_type (enum), difficulty (EASY/MEDIUM/HARD), prep_time_minutes, servings, ingredients (linked list of (Ingredient, quantity) pairs) |
| **Supplier (供应商)** | supplier_id, name, location, reliability_score (0.0-1.0) |

### 2. Core Data Structures & Functionality (核心数据结构与功能)

#### Task 2: Recipe Catalogue (Binary Search Tree - BST) (食谱目录 - 二叉搜索树)

- **Implementation**: BST keyed on recipe name (alphabetical order)
- **Supported Operations (支持操作)**:
  - Insert new recipes (插入新食谱)
  - Search recipes by name (按名称搜索食谱)
  - Find all recipes of a given cuisine type (按菜系筛选食谱)
  - Find recipes achievable with current stock (cross-traversal with ingredient linked lists) (查找当前库存可制作的食谱)
  - Range search (recipes between two alphabetical letters) (字母范围搜索)
- **Key Questions Addressed (解决的关键问题)**:
  - Performance advantages over plain lists for search operations (搜索性能优势)
  - Worst-case time complexity analysis (最坏时间复杂度分析)
  - Scenarios for replacement with AVL Tree (self-balancing BST) (AVL树替代场景)

#### Task 3: Recipe Ingredients (Singly Linked List) (食谱食材 - 单向链表)

- **Implementation**: Linked list of (Ingredient, quantity) pairs for each recipe
- **Supported Operations (支持操作)**:
  - Add/remove ingredients (添加/删除食材)
  - Update ingredient quantities (更新食材数量)
  - Calculate total recipe cost (traversal + price lookup) (计算食谱总成本)
  - Check recipe feasibility (against current stock levels) (检查食谱可行性)
- **Key Questions Addressed (解决的关键问题)**:
  - Justification for linked list vs. Python list (链表 vs Python列表的选择理由)
  - Scenarios where Python list would be more optimal (Python列表更优的场景)

#### Task 4: Supply Network (Weighted Directed Graph) (供应网络 - 带权有向图)

- **Implementation**: Graph model where:
  - Nodes = Suppliers (节点 = 供应商)
  - Edges = Ingredient supply relationships (from supplier to company) (边 = 食材供应关系)
  - Edge weights = Cost per unit of ingredient (边权重 = 食材单位成本)
- **Supported Operations (支持操作)**:
  - Add/remove suppliers (添加/删除供应商)
  - Add/remove supply relationships (添加/删除供应关系)
  - Find all suppliers for a specific ingredient (查找食材的所有供应商)
  - Find cheapest supplier for an ingredient (查找食材的最便宜供应商)
  - Find all ingredients available within a cost budget (预算内食材筛选)

#### Task 5: Procurement Priority (Max-Heap) (采购优先级 - 最大堆)

- **Implementation**: Max-heap of ingredients needing restocking, keyed by urgency score
- **Urgency Score Formula (紧急度计算公式)**:
  ```
  Urgency = (minimum_stock - current_stock) * recipe_dependency_count + (1 / supplier_lead_time)
  ```
  *(Combines stock deficit, recipe dependency, and supplier lead time)*
- **Supported Operations (支持操作)**:
  - Add ingredients to procurement queue (添加食材到采购队列)
  - Remove highest-urgency item (移除最高紧急度食材)
  - Update urgency scores post-restocking (补货后更新紧急度)
  - List top-K most urgent items (列出前K个最紧急食材)

### 3. Dataset Generation & Loading (数据集生成与加载)

#### Dataset Requirements (数据集要求)

Generate realistic CSV datasets with minimum requirements:
- 15+ recipes (at least 3 cuisines, 2 difficulty levels) (15+个食谱，至少3种菜系，2种难度)
- 20+ ingredients (at least 5 below minimum stock, 3+ with multiple suppliers) (20+种食材，至少5种低于最低库存，3+种有多个供应商)
- 6+ suppliers (6+个供应商)
- 30+ supply relationships (30+个供应关系)

#### CSV File Structure (CSV文件结构)

| File Name | Columns |
|-----------|---------|
| recipes_dataset.csv | recipe_id, name, cuisine_type, difficulty, prep_time_minutes, servings |
| ingredients_dataset.csv | ingredient_id, name, category, unit, current_stock, minimum_stock |
| suppliers_dataset.csv | supplier_id, name, location, reliability_score |
| supply_relationships_dataset.csv | supplier_id, ingredient_id, cost_per_unit |

#### Loading Process (加载流程)

1. Load all four CSV files into the system (加载四个CSV文件)
2. Construct core data structures:
   - BST from recipe data (从食谱数据构建BST)
   - Linked lists for recipe ingredients (构建食谱食材链表)
   - Supply network graph (构建供应网络图)
   - Procurement priority heap (构建采购优先级堆)

### 4. Advanced Algorithms (高级算法)

#### Substitution Graph (食材替换图)

- Build substitution relationships between ingredients (构建食材替换关系)
- Find all substitutes for a given ingredient (查找食材的所有替代品)
- Check recipe feasibility with substitutions (考虑替代方案的食谱可行性)

#### Supplier Optimizer (供应商优化器)

- Find minimum cost supplier combination for a recipe (查找食谱的最低成本供应商组合)
- Filter suppliers by reliability threshold (按可靠性阈值筛选供应商)

#### Weekly Menu Planner (周菜单规划器)

- Analyze weekly menu feasibility (分析周菜单可行性)
- Identify ingredient shortages (识别食材短缺)

#### Supply Crisis Recovery (供应链危机恢复)

- Simulate supplier shutdown scenarios (模拟供应商断供场景)
- Scan risk recipes (扫描风险食谱)
- Generate recovery plans (生成恢复方案)

## Testing Requirements (测试要求)

All functionality must be verified using `unittest` framework with the following critical tests:

### Part1 Tests (基础数据结构测试)
1. BST in-order traversal returns recipe names in alphabetical order (BST中序遍历验证)
2. Each recipe's ingredient linked list length matches loaded supply relationships (链表长度验证)
3. Procurement heap correctly returns highest-urgency ingredient first (堆优先级验证)
4. Supply graph accurately identifies all suppliers for a given ingredient (供应图验证)

### Part2 Tests (高级算法测试)
1. Substitution graph search (食材替换图搜索)
2. Optimal supplier cost calculation (最优供应商成本计算)
3. Weekly menu planning (周菜单规划)
4. Performance benchmark (性能基准测试)

### Part3 Tests (危机恢复测试)
1. Supplier shutdown simulation (供应商断供模拟)
2. Risk recipe scanning (风险食谱扫描)
3. Recovery plan generation (恢复方案生成)

## Technical Stack (技术栈)

| Category | Technology |
|----------|------------|
| Programming Language | Python 3.10+ |
| Core Concepts | Data Structures (BST, Linked List, Graph, Heap), Algorithm Design, CSV Handling, Unit Testing |
| Visualization | Tkinter GUI, Matplotlib Charts |
| Testing | unittest Framework |
| Dependencies | matplotlib>=3.7, Pillow>=9.0 |

## Usage Instructions (使用说明)

### Quick Start (快速开始)

```bash
# Install dependencies (安装依赖)
pip install -r requirements.txt

# Run the main program (运行主程序)
python main.py
```

The system will automatically:
1. Generate datasets (生成数据集)
2. Run all modules (Part1, Part2, Part3) sequentially (依次运行所有模块)
3. Launch the visualization GUI (启动可视化GUI)

### Manual Testing (手动测试)

```bash
# Run Part1 tests (运行Part1测试)
python -m unittest test_part1.py

# Run Part2 tests (运行Part2测试)
python -m unittest test_part2.py

# Run Part3 tests (运行Part3测试)
python -m unittest test_part3.py

# Run all tests (运行所有测试)
python -m unittest discover -v
```

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
│   │   ├── linked_list.py     # Singly Linked List (单向链表)
│   │   ├── max_heap.py        # Max-Heap (最大堆)
│   │   ├── supply_graph.py    # Supply Network Graph (供应网络图)
│   │   ├── dataset_generator.py # Dataset Generator (数据集生成器)
│   │   └── models.py          # Data Models (数据模型)
│   ├── part2/                 # Advanced Algorithms (高级算法)
│   │   ├── substitution_graph.py # Substitution Graph (食材替换图)
│   │   ├── supplier_optimizer.py # Supplier Optimizer (供应商优化器)
│   │   ├── weekly_menu_planner.py # Weekly Menu Planner (周菜单规划器)
│   │   ├── benchmark.py       # Performance Benchmark (性能基准测试)
│   │   └── gui_app.py         # Visualization GUI (可视化GUI)
│   └── part3/                 # Crisis Recovery (危机恢复)
│       └── supply_crisis_recovery.py # Supply Crisis Recovery (供应链危机恢复)
├── test_part1.py              # Part1 Unit Tests (Part1单元测试)
├── test_part2.py              # Part2 Unit Tests (Part2单元测试)
└── test_part3.py              # Part3 Unit Tests (Part3单元测试)
```

## Key Performance Considerations (关键性能考虑)

- **BST** provides O(log n) average search time (vs O(n) for lists)
- **Linked Lists** enable efficient insertion/deletion of recipe ingredients
- **Graph Traversal** algorithms optimize supplier selection
- **Heap Structure** ensures O(1) access to highest-priority procurement items

## GUI Features (GUI功能)

The visualization panel includes 7 tabs:
1. **Recipe Search (食谱搜索)** - Search recipe by name, view details
2. **Cuisine Filter (菜系筛选)** - Filter recipes by cuisine type
3. **Alphabet Range (字母范围搜索)** - Search recipes by alphabet range
4. **Ingredient Substitution (食材替换)** - Query ingredient substitutes
5. **Supply Network (供应网络)** - Query ingredient suppliers
6. **Performance Chart (性能图表)** - View benchmark visualization
7. **Test Results (测试结果)** - Run all tests with detailed report

## Summary (总结)

This system leverages four fundamental data structures to solve distinct catering business challenges:
- **BST** optimizes recipe search (优化食谱搜索)
- **Linked Lists** manage recipe ingredients (管理食谱食材)
- **Graphs** model supplier networks (建模供应商网络)
- **Heaps** prioritize procurement (优先采购)
