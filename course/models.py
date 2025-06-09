from typing import Optional, List
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import UniqueConstraint
from enum import Enum
from pydantic import BaseModel

# Tables

class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str
    levels: List["MainLevel"] = Relationship(back_populates="course")


class MainLevel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    course_id: int = Field(foreign_key="course.id")
    course: Course = Relationship(back_populates="levels")
    categories: List["Category"] = Relationship(back_populates="main_level")


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    main_level_id: int = Field(foreign_key="mainlevel.id")
    main_level: MainLevel = Relationship(back_populates="categories")
    items: List["Item"] = Relationship(back_populates="category")

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    category_id: int = Field(foreign_key="category.id")
    category: Category = Relationship(back_populates="items")

# Models

class MainLevelName(str,Enum):
    beginner = 'BEGINNER'
    intermediate = 'INTERMEDIATE'
    advance = 'ADVANCE'

class CategoryName(str,Enum):
    exercise = 'EXERCISE'
    reference = 'REFERENCE'

class ItemCreate(BaseModel):
    name: str  # maps to `content` in DB

class CategoryCreate(BaseModel):
    name: CategoryName
    items: List[ItemCreate]

class LevelCreate(BaseModel):
    name: MainLevelName
    categories: List[CategoryCreate]

class CourseCreate(BaseModel):
    title: str
    description: str
    levels: List[LevelCreate]

def serialize_course(course):
    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "levels": [
            {
                "id": level.id,
                "name": level.name,
                "categories": [
                    {
                        "id": category.id,
                        "name": category.name,
                        "items": [
                            {
                                "id": item.id,
                                "name": item.content,
                            }
                            for item in category.items
                        ],
                    }
                    for category in level.categories
                ],
            }
            for level in course.levels
        ],
    }
