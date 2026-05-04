from sqlalchemy import text
from app.api.deps import get_current_user


def test_apply_rls_context_sets_postgres_session_values(db, test_user, test_token):
    current_user = get_current_user(token=test_token, db=db)

    current_user_id = db.execute(
        text("SELECT current_setting('app.current_user_id', true)")
    ).scalar_one()
    current_user_role = db.execute(
        text("SELECT current_setting('app.current_user_role', true)")
    ).scalar_one()

    assert current_user.id == test_user.id
    assert current_user_id == str(test_user.id)
    assert current_user_role == test_user.role.value
