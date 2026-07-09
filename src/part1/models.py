from enum import Enum
from typing import List, Tuple, Optional


# 食材分类枚举（补充LIQUID类型，修复运行时引用错误）
class IngredientCategory(Enum):
    PRODUCE = "PRODUCE"  # 生鲜果蔬
    DAIRY = "DAIRY"      # 乳制品
    MEAT = "MEAT"        # 肉类
    GRAIN = "GRAIN"      # 谷物
    SPICE = "SPICE"      # 调味品
    LIQUID = "LIQUID"    # 液体类（新增，修复dataset_generator中引用问题）


# 菜系枚举
class CuisineType(Enum):
    CHINESE = "CHINESE"  # 中餐
    WESTERN = "WESTERN"  # 西餐
    JAPANESE = "JAPANESE"# 日料
    THAI = "THAI"        # 泰餐


# 难度枚举
class Difficulty(Enum):
    EASY = "EASY"        # 简单
    MEDIUM = "MEDIUM"    # 中等
    HARD = "HARD"        # 困难


class Ingredient:
    """
    食材实体类，描述餐饮企业的食材属性

    Attributes:
        ingredient_id (int): 食材唯一标识
        name (str): 食材名称
        category (IngredientCategory): 食材分类（枚举）
        unit (str): 计量单位（如kg/L）
        current_stock (float): 当前库存数量
        minimum_stock (float): 最低库存阈值
        lead_time (int): 供应商交货提前期（天），默认7天

    Methods:
        stock_shortage: 计算库存缺口（低于最低库存为正数）
    """

    def __init__(
        self,
        ingredient_id: int,
        name: str,
        category: IngredientCategory,
        unit: str,
        current_stock: float,
        minimum_stock: float,
        lead_time: int = 7
    ):
        self.ingredient_id = ingredient_id
        self.name = name
        self.category = category
        self.unit = unit
        self.current_stock = current_stock
        self.minimum_stock = minimum_stock
        self.lead_time = lead_time  # 交货提前期，用于紧急度计算

    def stock_shortage(self) -> float:
        """
        计算食材库存缺口：若当前库存 < 最低库存，返回缺口值；否则返回0

        Returns:
            float: 库存缺口（非负数）
        """
        return max(0.0, self.minimum_stock - self.current_stock)

    def __repr__(self) -> str:
        return (
            f"<Ingredient(id={self.ingredient_id}, name={self.name}, "
            f"category={self.category.value}, stock={self.current_stock}/{self.minimum_stock}{self.unit})>"
        )


class Recipe:
    """
    食谱实体类，描述餐饮企业的食谱属性

    Attributes:
        recipe_id (int): 食谱唯一标识
        name (str): 食谱名称
        cuisine_type (CuisineType): 菜系（枚举）
        difficulty (Difficulty): 制作难度（枚举）
        prep_time_minutes (int): 准备时间（分钟）
        servings (int): 适用人数
        ingredient_list (Optional[RecipeIngredientLinkedList]): 食材链表（(Ingredient, quantity)对）

    Methods:
        __repr__: 自定义打印格式
    """

    def __init__(
        self,
        recipe_id: int,
        name: str,
        cuisine_type: CuisineType,
        difficulty: Difficulty,
        prep_time_minutes: int,
        servings: int
    ):
        self.recipe_id = recipe_id
        self.name = name
        self.cuisine_type = cuisine_type
        self.difficulty = difficulty
        self.prep_time_minutes = prep_time_minutes
        self.servings = servings
        self.ingredient_list: Optional[RecipeIngredientLinkedList] = None  # 挂载单向链表

    def __repr__(self) -> str:
        return (
            f"<Recipe(id={self.recipe_id}, name={self.name}, "
            f"cuisine={self.cuisine_type.value}, difficulty={self.difficulty.value})>"
        )


class Supplier:
    """
    供应商实体类，描述食材供应商属性

    Attributes:
        supplier_id (int): 供应商唯一标识
        name (str): 供应商名称
        location (str): 供应商所在地
        reliability_score (float): 可靠性评分（0.0~1.0）

    Methods:
        __repr__: 自定义打印格式
    """

    def __init__(
        self,
        supplier_id: int,
        name: str,
        location: str,
        reliability_score: float
    ):
        # 校验可靠性评分范围
        if not (0.0 <= reliability_score <= 1.0):
            raise ValueError(f"可靠性评分{reliability_score}必须在0.0~1.0之间")
        self.supplier_id = supplier_id
        self.name = name
        self.location = location
        self.reliability_score = reliability_score

    def __repr__(self) -> str:
        return (
            f"<Supplier(id={self.supplier_id}, name={self.name}, "
            f"location={self.location}, reliability={self.reliability_score:.2f})>"
        )


