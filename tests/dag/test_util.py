from unittest.mock import Mock
from pathlib import Path

import pytest

from ploomber import DAG
from ploomber.tasks import PythonCallable, SQLScript
from ploomber.products import (File, SQLRelation, SQLiteRelation,
                               GenericSQLRelation, PostgresRelation)
from ploomber.exceptions import DAGRenderError


def touch_root(product):
    Path(str(product)).touch()


def touch(upstream, product):
    Path(str(product)).touch()


def test_duplicated_files():
    dag = DAG()
    PythonCallable(touch_root, File('a'), dag, name='task')
    PythonCallable(touch_root, File('a'), dag, name='another')

    with pytest.raises(DAGRenderError) as excinfo:
        dag.render()

    expected = ("Tasks must generate unique Products. "
                "The following Products appear in more than one task "
                "{File('a'): ['task', 'another']}")

    assert expected == str(excinfo.value)


def test_duplicated_files_one_absolute():
    dag = DAG()
    PythonCallable(touch_root, File('a'), dag, name='task')
    PythonCallable(touch_root, File(Path('a').resolve()), dag, name='another')

    with pytest.raises(DAGRenderError) as excinfo:
        dag.render()

    expected = ("Tasks must generate unique Products. "
                "The following Products appear in more than one task "
                "{File('a'): ['task', 'another']}")

    assert expected == str(excinfo.value)


def test_duplicated_files_metaproduct():
    dag = DAG()
    PythonCallable(touch_root, File('a'), dag, name='task')
    PythonCallable(touch_root, {
        'product': File('a'),
        'another': File('b')
    },
                   dag,
                   name='another')

    with pytest.raises(DAGRenderError) as excinfo:
        dag.render()

    expected = ("Tasks must generate unique Products. "
                "The following Products appear in more than one task "
                "{File('a'): ['task', 'another']}")

    assert expected == str(excinfo.value)


@pytest.mark.parametrize('class1, class2, return_value', [
    [SQLRelation, SQLRelation, [[], True]],
    [SQLiteRelation, SQLiteRelation, []],
    [GenericSQLRelation, GenericSQLRelation, []],
    [PostgresRelation, PostgresRelation, [[], True]],
    [PostgresRelation, SQLRelation, [[], True]],
],
                         ids=[
                             'sqlrelation',
                             'sqliterelation',
                             'genericsqlrelation',
                             'postgresrelation',
                             'mix',
                         ])
def test_duplicated_sql_product(class1, class2, return_value):
    dag = DAG()

    client = Mock()
    client.split_source = ';'
    client.connection.cursor().fetchone.return_value = return_value

    dag.clients[SQLScript] = client
    dag.clients[class1] = client
    dag.clients[class2] = client

    SQLScript('CREATE TABLE {{product}} AS SELECT * FROM table',
              class1(('schema', 'name', 'table')),
              dag=dag,
              name='task')
    SQLScript('CREATE TABLE {{product}} AS SELECT * FROM table',
              class2(('schema', 'name', 'table')),
              dag=dag,
              name='another')

    with pytest.raises(DAGRenderError) as excinfo:
        dag.render()

    assert 'Tasks must generate unique Products.' in str(excinfo.value)
