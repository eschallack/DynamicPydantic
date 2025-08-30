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
from sqlalchemy_to_json_schema.schema_factory import Schema as JsonSchema
from sqlalchemy_to_json_schema.walkers import StructuralWalker, ForeignKeyWalker 
from datamodel_code_generator import DataModelType, PythonVersion
from datamodel_code_generator.model import get_data_model_types
from datamodel_code_generator.parser.jsonschema import JsonSchemaParser
from typing import Type, Any
from pydantic.v1 import BaseModel
from pydantic.v1.main import ModelMetaclass
from pathlib import Path
from abc import ABC
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

def attach_code_method_to_pydantic_class(cls:BaseModel, code_str:str) -> BaseModel:
    cls.codegen = CodeExporter(code_str)
    return cls

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
    table_obj.name
    class TableObj(Base):
        __table__ = table_obj
        
        Base
    return TableObj

def sqlalchemy_jsonschema(Model:DeclarativeMeta,fk=True) -> JsonSchema:
    if fk:
        wkr = ForeignKeyWalker
    else:
        wkr = StructuralWalker
    factory = SchemaFactory(wkr)
    json_schema= factory(Model)
    json_schema['title'] = Model.__table__.name
    return json_schema

def jsonschema_pydantic(json_schema:JsonSchema|dict[Any,Any]) -> tuple[BaseModel, str]:
    
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
    cls = None
    for k, v in ex_namespace.items():
        v_type = type(v)
        if isinstance(v, ModelMetaclass):
            cls = v
    if not cls:
        raise Exception("Class not found in output")      
    cls.__module__ = __name__
    return attach_code_method_to_pydantic_class(cls,code_str)

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
    return jsonschema_pydantic(json_schema)

def table_to_pydantic(connection_str:str, table:str,schema:str=None, fk:bool=True) -> BaseModel:
    sqlalchemy_model=table_to_sqlalchemy(connection_str,table,schema=schema)
    return sqlalchemy_pydantic(sqlalchemy_model,fk=fk)

if __name__ == '__main__':
    from sqlalchemytopydantic import DB_CONNECTION_STR
    MyTable=table_to_sqlalchemy("mysql+pymysql://admin:admin@localhost:3306/employees","employees")
    PydModel=sqlalchemy_pydantic(MyTable)
    print(PydModel.codegen)
    PydModel.codegen.export(rf'example/output/{PydModel.class_name}.py')