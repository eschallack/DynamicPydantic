# Example: sql table to pydantic class
from sqlalchemytopydantic import table_to_pydantic, DB_CONNECTION_STR

PydModel=table_to_pydantic(DB_CONNECTION_STR,"employees")
print(PydModel.codegen)
PydModel.codegen.export(rf'example/output/{PydModel.__name__}.py')