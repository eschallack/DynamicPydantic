from dynamicpydantic import jsonschema_pydantic
json_schema={
    'title': 'employees_auto', 
    'type': 'object', 
    'properties': {
        'emp_no': {'type': 'integer'}, 
        'birth_date': {'type': 'string', 'format': 'date'},
        'first_name': {'type': 'string', 'maxLength': 14},
        'last_name': {'type': 'string', 'maxLength': 16},
        'gender': {'type': 'string', 'maxLength': 1, 'enum': ['M', 'F']}, 
        'hire_date': {'type': 'string', 'format': 'date'
        }
    }, 'required': [
        'birth_date', 
        'emp_no', 
        'first_name', 
        'gender', 
        'hire_date', 
        'last_name'
    ]
}
PydModel = jsonschema_pydantic(json_schema)
print(PydModel.__fields__)
PydModel.codegen.export(rf'example/output/{PydModel.__name__}.py')
