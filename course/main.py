from fastapi import FastAPI, Depends, Query, Path, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.orm import selectinload
from typing import Annotated
from json import dumps

from .models import Course,MainLevel,Category,Item,CourseCreate,MainLevelName,CategoryName, serialize_course
# from fastapi.security.

import uvicorn

app = FastAPI()

sqlite_file_name = 'course1.db'
sqlite_url = f'sqlite:///{sqlite_file_name}'

connect_args = {'check_same_thread': False}
engine = create_engine(sqlite_url, connect_args=connect_args)


# DATABASE_URL = "mysql+pymysql://admin:admintest@ld77.ci9mca82oykl.us-east-1.rds.amazonaws.com:3306/ld-dev"
# engine = create_engine(DATABASE_URL, echo=False)





def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]



@app.on_event('startup')
def on_startup():
    create_db_and_tables()

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get('/courses',tags=['Course'])
def course_list(session:SessionDep,
                offset:int=0,
                limit:Annotated[int,Query(le=100)]=100
                ):
    statement = select(Course).options(
            selectinload(Course.levels),
            selectinload(Course.levels).selectinload(MainLevel.categories),
            selectinload(Course.levels).selectinload(MainLevel.categories).selectinload(Category.items)
        ).offset(offset).limit(limit)
    courses = session.exec(statement).all()
    total_count = len(session.exec(select(Course)).all())
    return {
        "totalCount": total_count,
        "limit": limit,
        "offset": offset,
        "data": [serialize_course(course) for course in courses]
    }

@app.get('/course/details/{id}',tags=['Course'])
def course_details(session:SessionDep,
                   id: Annotated[int,Path(title='id of the course to get for details')]):
    statement = select(Course).options(
            selectinload(Course.levels),
            selectinload(Course.levels).selectinload(MainLevel.categories),
            selectinload(Course.levels).selectinload(MainLevel.categories).selectinload(Category.items)
        ).where(Course.id == id)
    courses = session.exec(statement).first()

    if not courses:
        raise HTTPException(status_code=404, detail='Course does not exists.')


    return serialize_course(courses)

@app.post('/course/create', tags=['Course'])
def create_course(session:SessionDep,course_data:CourseCreate):
    course = Course(title=course_data.title, description=course_data.description)

    level_names = [level.name for level in course_data.levels]

    # Duplicate Check for Levels
    if len(set(level_names)) != len(level_names):
        raise HTTPException(
            status_code=400,
            detail="Duplicate level are not allowed within the same course."
        )

    for level_data in course_data.levels:
        level = MainLevel(name=level_data.name, course=course)

        for category_data in level_data.categories:
            category_names = [c.name for c in level_data.categories]

            # Duplicate Check for Categories
            if len(set(category_names)) != len(category_names):
                raise HTTPException(
                    status_code=400,
                    detail=f"Duplicate category names in level '{level_data.name.value}'."
                )

            category = Category(name=category_data.name, main_level=level)

            for item_data in category_data.items:
                item = Item(content=item_data.name, category=category)
                category.items.append(item)
            level.categories.append(category)

        course.levels.append(level)

    session.add(course)
    session.commit()
    session.refresh(course)

    return {"message": "Course created successfully"}

# if __name__ == '__main__':
#     uvicorn.run(app, port=8082, host= '0.0.0.0')