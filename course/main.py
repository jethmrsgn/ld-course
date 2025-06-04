from fastapi import FastAPI, Depends, Query, Path, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.orm import selectinload
from typing import Annotated
from json import dumps

from models import Course,MainLevel,Category,Item, serialize_course
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

if __name__ == '__main__':
    uvicorn.run(app, port=8082, host= '0.0.0.0')