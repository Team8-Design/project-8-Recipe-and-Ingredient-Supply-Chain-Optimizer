# Catering Company Recipe & Ingredient Management System
A comprehensive software solution for catering companies to manage recipes, ingredients, suppliers, and procurement using core data structures (BST, Linked List, Graph, Heap).

## Project Overview
This system is designed to address the key operational needs of a catering company:
- Organize recipe catalogs for efficient searching
- Optimize ingredient sourcing (cheapest/nearest/most reliable supplier)
- Detect possible ingredient substitutions
- Manage weekly procurement priority lists
- Leverage four fundamental data structures with distinct roles in the system architecture

## System Architecture & Core Components
### 1. Data Models
The system is built around three core entities with well-defined attributes:

| Entity | Key Attributes |
|--------|----------------|
| **Ingredient** | ingredient_id, name, category (PRODUCE/DAIRY/MEAT/GRAIN/SPICE), unit, current_stock, minimum_stock |
| **Recipe** | recipe_id, name, cuisine_type (enum), difficulty (EASY/MEDIUM/HARD), prep_time_minutes, servings, ingredients (linked list of (Ingredient, quantity) pairs) |
| **Supplier** | supplier_id, name, location, reliability_score (0.0-1.0) |

### 2. Core Data Structures & Functionality
#### Task 2: Recipe Catalogue (Binary Search Tree - BST)
- **Implementation**: BST keyed on recipe name (alphabetical order)
- **Supported Operations**:
  - Insert new recipes
  - Search recipes by name
  - Find all recipes of a given cuisine type
  - Find recipes achievable with current stock (cross-traversal with ingredient linked lists)
  - Range search (recipes between two alphabetical letters)
- **Key Questions Addressed**:
  - Performance advantages over plain lists for search operations
  - Worst-case time complexity analysis
  - Scenarios for replacement with AVL Tree (self-balancing BST)

#### Task 3: Recipe Ingredients (Singly Linked List)
- **Implementation**: Linked list of (Ingredient, quantity) pairs for each recipe
- **Supported Operations**:
  - Add/remove ingredients
  - Update ingredient quantities
  - Calculate total recipe cost (traversal + price lookup)
  - Check recipe feasibility (against current stock levels)
- **Key Questions Addressed**:
  - Justification for linked list vs. Python list
  - Scenarios where Python list would be more optimal

#### Task 4: Supply Network (Weighted Directed Graph)
- **Implementation**: Graph model where:
  - Nodes = Suppliers
  - Edges = Ingredient supply relationships (from supplier to company)
  - Edge weights = Cost per unit of ingredient
- **Supported Operations**:
  - Add/remove suppliers
  - Add/remove supply relationships
  - Find all suppliers for a specific ingredient
  - Find cheapest supplier for an ingredient
  - Find all ingredients available within a cost budget

#### Task 5: Procurement Priority (Max-Heap)
- **Implementation**: Max-heap of ingredients needing restocking, keyed by urgency score
- **Urgency Score Formula** (custom definition):
  ```
  Urgency = (minimum_stock - current_stock) * recipe_dependency_count + (1 / supplier_lead_time)
  ```
  *(Combines stock deficit, recipe dependency, and supplier lead time)*
- **Supported Operations**:
  - Add ingredients to procurement queue
  - Remove highest-urgency item
  - Update urgency scores post-restocking
  - List top-K most urgent items

### 3. Dataset Generation & Loading (Task 6)
#### Dataset Requirements
Generate realistic CSV datasets with minimum requirements:
- 15+ recipes (at least 3 cuisines, 2 difficulty levels)
- 20+ ingredients (at least 5 below minimum stock, 3+ with multiple suppliers)
- 6+ suppliers
- 30+ supply relationships

#### CSV File Structure
| File Name | Columns |
|-----------|---------|
| recipes_dataset.csv | recipe_id, name, cuisine_type, difficulty, prep_time_minutes, servings |
| ingredients_dataset.csv | ingredient_id, name, category, unit, current_stock, minimum_stock |
| suppliers_dataset.csv | supplier_id, name, location, reliability_score |
| supply_relationships_dataset.csv | supplier_id, ingredient_id, cost_per_unit |

#### Loading Process
1. Load all four CSV files into the system
2. Construct core data structures:
   - BST from recipe data
   - Linked lists for recipe ingredients
   - Supply network graph
   - Procurement priority heap

## Testing Requirements
All functionality must be verified using `unittest` framework with the following critical tests:
1. BST in-order traversal returns recipe names in alphabetical order
2. Each recipe's ingredient linked list length matches loaded supply relationships
3. Procurement heap correctly returns highest-urgency ingredient first
4. Supply graph accurately identifies all suppliers for a given ingredient

## Technical Stack
- Programming Language: Python
- Core Concepts: Data Structures (BST, Linked List, Graph, Heap), Algorithm Design, CSV Handling, Unit Testing
- No external dependencies (pure Python implementation)

## Usage Instructions
1. **Generate Datasets**: Run the dataset generator script to create the four required CSV files
2. **Load Data**: Execute the data loading module to initialize all data structures
3. **Core Operations**: Use the respective methods for:
   - Recipe search/management (BST operations)
   - Ingredient list modification (Linked List operations)
   - Supplier optimization (Graph traversal)
   - Procurement planning (Heap operations)
4. **Run Tests**: Execute the test suite to validate all core functionality

## Key Performance Considerations
- BST provides O(log n) average search time (vs O(n) for lists)
- Linked lists enable efficient insertion/deletion of recipe ingredients
- Graph traversal algorithms optimize supplier selection
- Heap structure ensures O(1) access to highest-priority procurement items

## Summary
- This system leverages four fundamental data structures to solve distinct catering business challenges
- The BST optimizes recipe search, Linked Lists manage recipe ingredients, Graphs model supplier networks, and Heaps prioritize procurement
- The solution includes comprehensive dataset generation, loading, and validation with unit tests
- The implementation addresses both functional requirements and theoretical analysis of data structure performance tradeoffs