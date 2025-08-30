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
