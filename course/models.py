from sqlmodel import SQLModel,Field

class Course(SQLModel, table=True):
	id: int = Field(default=None,primary_key=True)
	title: str = Field(index=True)
	description: str
	points: int | None = None
