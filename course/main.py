from fastapi import FastAPI, Depends, Query, Path, HTTPException
from sqlmodel import Session, SQLModel, create_engine, select
from typing import Annotated

from models import Course
# from fastapi.security.

import uvicorn

app = FastAPI()

sqlite_file_name = 'course.db'
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


@app.get('/courses',tags=['Course'])
def course_list(session:SessionDep,
                offset:int=0,
                limit:Annotated[int,Query(le=100)]=100
                )-> list[Course]:
    courses = session.exec(select(Course).offset(offset).limit(limit)).all()
    return courses

@app.get('/course/details/{id}',tags=['Course'])
def course_details(session:SessionDep,
                   id: Annotated[int,Path(title='Title of the course to get for details')])-> Course:
    statement = select(Course).where(Course.id == id)
    course = session.exec(statement).first()

    if not course:
        raise HTTPException(status_code=404, detail='Course does not exists.')

    return course

# if __name__ == '__main__':
#     uvicorn.run(app, port=8000, host= '0.0.0.0')