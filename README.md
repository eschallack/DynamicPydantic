# SQLAlchemyToPydantic
Create Pydantic models from Json Schema to SQLAlchemy models with complex datatypes, dynamically at runtime.

## Usage

Quick Example:

```Python
from sqlalchemytopydantic import table_to_pydantic, DB_CONNECTION_STR

PydModel=table_to_pydantic(DB_CONNECTION_STR,"employees")
print(PydModel.__fields__)
```
```text
{'emp_no': ModelField(name='emp_no', type=int, required=True), 'birth_date': ModelField(name='birth_date', type=date, required=True), 'first_name': ModelField(name='first_name', type=ConstrainedStrValue, required=True), 'last_name': ModelField(name='last_name', type=ConstrainedStrValue, required=True), 'gender': ModelField(name='gender', type=Gender, required=True), 'hire_date': ModelField(name='hire_date', type=date, required=True)}
```
Code generation Example:
```Python
from sqlalchemytopydantic import table_to_pydantic, DB_CONNECTION_STR

PydModel=table_to_pydantic(DB_CONNECTION_STR,"employees")
print(PydModel.codegen)
PydModel.codegen.export(rf'example/output/{PydModel.__name__}.py')
```
```text
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
```

This library combines functionality from datamodel-code-generator and sqlalcehmy-to-json-schema to create schemas on the fly with some modifications
to datamodel-code-generator's parser logic.