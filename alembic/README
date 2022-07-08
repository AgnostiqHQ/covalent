# DB Migration Guide

## Getting Started

When first getting started, we need to generate our initial set of migrations (that is, generate scripts that will update the database schema to correspond to our DB models `covalent/_data_store/models.py`).

We do this by running the following in the project root of covalent

```bash
alembic revision — autogenerate -m "init"
```

You should see a new python file generated under `alembic/versions`. Also, there should be a table name in the database called `alembic_version` which will keep track of which migrations have run corresponding to the filenames in `alembic/versions`.

> The python files in `alembic/versions` contain an `upgrade()` method which will sync our database schema with our DB models `covalent/_data_store/models.py`. Furthermore, it contains a `downgrade()` command which will undo the operations performed by `upgrade()`. We do not explicitly call these methods, this is done by the alembic cli.

## Run Migrations

To now run the migrations which we have not yet run we execute

```bash
alembic upgrade head
```

To see history of which migrations we have run we can execute

```bash
alembic history
```

## Generate Migrations

To generate new migrations as a result of editing our DB model files, we can run the following

```bash
alembic revision — autogenerate -m "Description of DB update"
```

Which will create a new version file under `alembic/versions` (*This will not run the migrations, it will just generate the version file*)

## Undo Migrations

To undo the last migration we can run

```bash
alembic downgrade -1
```

Alternatively we can specify the exact version which we want to revert to (we can use `alembic history` for this)

```bash
alembic downgrade 1ed41b6d3f3f
```
