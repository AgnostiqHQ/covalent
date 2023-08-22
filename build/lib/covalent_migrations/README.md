# DB Migration Guide

## Getting Started & Running Migrations

Whenever merging other branches into your working branch always remember to run migrations as the database schema may have changed.

In order to update the DB to reflect the most up to date DB models we run the migrations (that have not yet run) as such:

```bash
covalent db alembic upgrade head
```

To see history of which migrations we have run we can execute

```bash
covalent db alembic history
```

## Autogenerate Migrations

To generate new migrations as a result of editing our DB model files, we can run the following

```bash
covalent db alembic revision --autogenerate -m "Description of DB update"
```


You should see a new python file generated under `alembic/versions`. Also, there should be a table name in the database called `alembic_version` which will keep track of which migrations have run corresponding to the filenames in `alembic/versions`.

> The python files in `alembic/versions` contain an `upgrade()` method which will sync our database schema with our DB models `covalent/_data_store/models.py`. Furthermore, it contains a `downgrade()` command which will undo the operations performed by `upgrade()`. We do not explicitly call these methods, this is done by the alembic cli.


## Generate Template Migration

To create a migration file which will be edited manually, one can run:

```bash
covalent db alembic revision -m "my custom migration file"
```

## Undo Migrations

To undo the last migration we can run

```bash
covalent db alembic downgrade -1
```

Alternatively we can specify the exact version which we want to revert to (we can use `alembic history` for this)

```bash
covalent db alembic downgrade 1ed41b6d3f3f
```
