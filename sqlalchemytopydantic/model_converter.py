import sys
import os
submodule_paths = [os.path.join(os.path.dirname(__file__), 'submodules', 'sqlalchemy-to-json-schema'),
                   os.path.join(os.path.dirname(__file__), 'submodules', 'datamodel-code-generator/src')]
for submodule_path in submodule_paths:
    if submodule_path not in sys.path:
        sys.path.append(submodule_path)
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import declarative_base, DeclarativeMeta
from sqlalchemy_to_json_schema.schema_factory import SchemaFactory, Schema
from sqlalchemy_to_json_schema.walkers import StructuralWalker, ForeignKeyWalker 
from datamodel_code_generator import DataModelType, PythonVersion
from datamodel_code_generator.model import get_data_model_types, pydantic
from datamodel_code_generator.parser.jsonschema import JsonSchemaParser
from typing import Type
from pydantic import BaseModel
import os
from pathlib import Path

class CodeExporter:
    """holds a pydantic model's code string and export it to a file."""
    def __init__(self, code_string: str) -> None:
        self.__codegen__ = code_string

    def __repr__(self) -> str:
        return self.__codegen__

    def export(self, output_path: str | Path) -> None:
        """Exports the code string to the specified file path."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(self.__codegen__)
            
def table_to_sqlalchemy(connection_str:str, table:str,schema:str=None) -> type[DeclarativeMeta]:
    """creates a table model from sql db params

    :param connection_str: your db connection string
    :type connection_str: str
    :param table: your table name
    :type table: str
    :param schema: schema name, if any, defaults to None
    :type schema: str, optional
    :return: A SQLAlchemy Representation of your table
    :rtype: DeclarativeMeta
    """
    engine = create_engine(connection_str)
    Base = declarative_base()
    metadata_obj = MetaData()

    table_obj = Table(
        table,
        metadata_obj,
        autoload_with=engine,
        schema=schema
    )
    class TableObj(Base):
        __table__ = table_obj
        Base
    return TableObj

def sqlalchemy_jsonschema(Model:DeclarativeMeta,fk=True) -> Schema:
    if fk:
        walker = ForeignKeyWalker
    else:
        walker = StructuralWalker
    factory = SchemaFactory(walker)
    return factory(Model)

def jsonschema_pydantic(json_schema:Schema) -> tuple[BaseModel, str]:
    data_model_types = get_data_model_types(
        DataModelType.PydanticBaseModel,
        target_python_version=PythonVersion.PY_312
    )
    parser = JsonSchemaParser(
        f"""{json_schema}""",
        data_model_type=data_model_types.data_model,
        data_model_root_type=data_model_types.root_model,
        data_model_field_type=data_model_types.field_model,
        data_type_manager_type=data_model_types.data_type_manager,
        dump_resolve_reference_action=data_model_types.dump_resolve_reference_action,
    )
    code_str=parser.parse().replace('from pydantic ','from pydantic.v1 ').replace('from __future__ import annotations\n\n','')
    ex_namespace = {}
    exec(code_str, ex_namespace, ex_namespace)
    cls=list(parser.sorted_data_models.values())[-1]
    cls.__module__ = __name__
    return cls, code_str

def attach_code_method_to_pydantic_class(cls:BaseModel, code_str:str) -> BaseModel:
    cls.code = CodeExporter(code_str)
    return cls

def sqlalchemy_pydantic(Model:DeclarativeMeta, 
                        fk:bool=True)-> Type[BaseModel]:
    """
    Converts SQLAlchemy Model to Pydantic Model
    
    :param Model: your sqlalchemymodel
    :type Model: DeclarativeMeta
    :param fk: wether or not you want the code to parse foreign keys
    :type fk: bool
    :return: a Pydantic Class representation of your model
    :rtype: type[BaseModel]
    """
    json_schema = sqlalchemy_jsonschema(Model, fk)
    pydantic_schema, pydantic_code = jsonschema_pydantic(json_schema)
    return attach_code_method_to_pydantic_class(pydantic_schema,pydantic_code)

if __name__ == '__main__':
    connection_string="mycooldb://username:pass@localhost:1234/db"
    tablename="tablename"
    connection_string="mysql+pymysql://admin:admin@localhost:3306/employees"
    tablename="employees"
    MyTable=table_to_sqlalchemy(connection_string,tablename)
    PydModel=sqlalchemy_pydantic(MyTable)
    print(PydModel.code)
    PydModel.code.export('output.py')