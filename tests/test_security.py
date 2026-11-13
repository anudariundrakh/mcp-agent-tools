import pytest

from src.server.tools.math_tool import MathSecurityError, calculate_expression
from src.server.tools.sql_tool import SQLSecurityError, query_database, validate_select_only


@pytest.mark.parametrize("payload", [
    "DROP TABLE inventory",
    "UPDATE inventory SET stock_quantity=0",
    "INSERT INTO inventory VALUES (99, 'X', 'Seattle', 1)",
    "SELECT * FROM orders; DROP TABLE inventory;--",
])
def test_sql_ddl_dml_rejection(payload):
    with pytest.raises(SQLSecurityError):
        validate_select_only(payload)


def test_math_ace_blocked():
    with pytest.raises(MathSecurityError):
        calculate_expression("__import__('os').listdir('.')")


def test_database_remains_intact_after_attack_attempts():
    out = query_database("SELECT stock_quantity FROM inventory WHERE sku='SKU-90210' AND city='Seattle'")
    assert "80" in out
