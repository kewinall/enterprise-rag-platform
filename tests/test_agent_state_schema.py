from app.agent.state import SCHEMA_SQL


def test_agent_state_schema_contains_durable_entities():
    assert "CREATE TABLE IF NOT EXISTS agent_session" in SCHEMA_SQL
    assert "CREATE TABLE IF NOT EXISTS agent_checkpoint" in SCHEMA_SQL
    assert "CREATE TABLE IF NOT EXISTS agent_job" in SCHEMA_SQL
    assert "CREATE TABLE IF NOT EXISTS agent_memory" in SCHEMA_SQL
