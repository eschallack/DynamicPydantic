# SQLAlchemyToPydantic
Create Pydantic models from SQLAlchemy models with complex datatypes, dynamically at runtime.

## Usage

example:

```Python
from sqlalchemytopydantic import table_to_pydantic, DB_CONNECTION_STR

model=table_to_pydantic(DB_CONNECTION_STR,"employees")

print(model.schema_json(indent=2))
print(model.code)
PydModel.code.export(rf'example/output/{PydModel.class_name}.py')
"""
from datetime import date
from enum import Enum

from pydantic.v1 import BaseModel, constr


class Gender(Enum):
    M = 'M'
    F = 'F'


class Employees(BaseModel):
    emp_no: int
    birth_date: date
    first_name: constr(max_length=14)
    last_name: constr(max_length=16)
    gender: Gender
    hire_date: date
"""
This library adds a feature the pydantic team would not - the ability to
[SQLModel](https://sqlmodel.tiangolo.com/)
[Pydantic-SQLAlchemy](https://github.com/tiangolo/pydantic-sqlalchemy)