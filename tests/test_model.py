# ###################### #
# UNDER CONSTRUCTION     #
# ###################### #

# This test config was yanked from another project of mine. Not workin yet!!

# TODO: 
#  - Add docker/podman config for spinning up dbs for testing
#  - Add test setup that spins up containers and adds tables to dbs
#  - Write tests that ensure complex data types and multiple pydantic classes are working


import pytest
from sqlalchemy import create_engine, inspect, MetaData, Table
from sqlalchemy.orm import declarative_base
import yaml

with open("config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)
cfg = cfg['tests']['db_connection']

metadata_obj = MetaData()
DB_CONFIGS = [
    pytest.param(
        {
            "engine_url":cfg['postgres']['engine_url'],
            "table_name": "person",
            "schema": "person",
            "expected_fields": [
                "businessentityid", "persontype", "namestyle", "title",
                "firstname", "middlename", "lastname", "suffix",
                "emailpromotion", "additionalcontactinfo", "demographics",
                "rowguid", "modifieddate"
            ],
        },
        id="postgresql"
    ),
    pytest.param(
        {
            "engine_url": cfg['mysql']['engine_url'],
            "table_name": "employees",
            "schema": None,
            "expected_fields": [
                "emp_no", "birth_date", "first_name", "last_name",
                "gender", "hire_date"
            ], 
        },
        id="mysql"
    ),
]

@pytest.mark.parametrize("db_config", DB_CONFIGS)
class TestDatabaseModels:
    """Groups tests that run against multiple database configurations."""

    @pytest.fixture()
    def engine(self, db_config):
        """Creates a single SQLAlchemy engine per database configuration."""
        return create_engine(db_config["engine_url"])

    @pytest.fixture()
    def sample_table(self, engine, db_config):
        """
        Generic fixture to reflect a table and create a declarative model class.
        """
        Base = declarative_base()
        table = Table(
            db_config["table_name"],
            metadata_obj,
            autoload_with=engine,
            schema=db_config.get("schema")
        )

        class TestTable(Base):
            __table__ = table

        return TestTable

    @pytest.fixture
    def expected_field_names(self, db_config):
        """Provides the list of expected field names for the current DB config."""
        return db_config["expected_fields"]