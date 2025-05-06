from datetime import datetime, timedelta, timezone

from app import db
from app.models import ActivityLog


def test_calculate_total_eco_points(db_session, fake_user):
    """
    Positive test case: Ensure total eco points are calculated correctly for a user.
    """
    # Add mock activity logs to the database
    activity1 = ActivityLog(email=fake_user.email, activity_type="walking", eco_points=50, date=datetime.now(timezone.utc))
    activity2 = ActivityLog(email=fake_user.email, activity_type="cycling", eco_points=30, date=datetime.now(timezone.utc))
    db_session.add_all([activity1, activity2])
    db_session.commit()

    # Query total eco points
    total_points = db_session.query(ActivityLog).filter_by(email=fake_user.email).with_entities(
        db.func.sum(ActivityLog.eco_points)
    ).scalar() or 0

    assert total_points == 80  # 50 + 30

#
# def test_calculate_total_eco_points_no_logs(db_session, fake_user):
#     """
#     Negative test case: Ensure total eco points are 0 when no activity logs exist for a user.
#     """
#     # Ensure no activity logs exist for the user
#     total_points = db_session.query(ActivityLog).filter_by(email=fake_user.email).with_entities(
#         db.func.sum(ActivityLog.eco_points)
#     ).scalar() or 0
#
#     assert total_points == 0  # No logs, so total points should be 0
#
#
# def test_average_steps_per_day(db_session, fake_user):
#     """
#     Positive test case: Ensure average steps per day are calculated correctly for walking activity.
#     """
#     # Add mock activity logs to the database
#     now = datetime(2024, 1, 1, 12, 0, 0)
#
#     activity1 = ActivityLog(email=fake_user.email, activity_type="walking", steps=1000, date=now - timedelta(days=1))
#     activity2 = ActivityLog(email=fake_user.email, activity_type="walking", steps=2000, date=now)
#     db_session.add_all([activity1, activity2])
#     db_session.commit()
#
#     # Query average steps per day
#     avg_steps = db_session.query(
#         db.func.avg(ActivityLog.steps)
#     ).filter_by(email=fake_user.email, activity_type="walking").scalar() or 0
#
#     assert avg_steps == 1500  # (1000 + 2000) / 2
#
#
# def test_average_steps_per_day_no_logs(db_session, fake_user):
#     """
#     Negative test case: Ensure average steps per day are 0 when no walking logs exist.
#     """
#     # Ensure no walking activity logs exist for the user
#     avg_steps = db_session.query(
#         db.func.avg(ActivityLog.steps)
#     ).filter_by(email=fake_user.email, activity_type="walking").scalar() or 0
#
#     assert avg_steps == 0  # No logs, so average steps should be 0
#
#
# def test_redeem_eco_points(db_session, fake_user):
#     """
#     Positive test case: Ensure eco points are deducted correctly when redeemed.
#     """
#     # Add mock activity logs to the database
#     activity1 = ActivityLog(email=fake_user.email, activity_type="walking", eco_points=50, date=datetime.now(timezone.utc))
#     activity2 = ActivityLog(email=fake_user.email, activity_type="cycling", eco_points=30, date=datetime.now(timezone.utc))
#     db_session.add_all([activity1, activity2])
#     db_session.commit()
#
#     # Redeem 60 eco points
#     redeem_points = 60
#     logs = ActivityLog.query.filter_by(email=fake_user.email).order_by(ActivityLog.date).all()
#     remaining = redeem_points
#     for log in logs:
#         if remaining <= 0:
#             break
#         if log.eco_points > 0:
#             if log.eco_points <= remaining:
#                 remaining -= log.eco_points
#                 log.eco_points = 0
#             else:
#                 log.eco_points -= remaining
#                 remaining = 0
#     db_session.commit()
#
#     # Verify remaining eco points
#     total_points = db_session.query(ActivityLog).filter_by(email=fake_user.email).with_entities(
#         db.func.sum(ActivityLog.eco_points)
#     ).scalar() or 0
#
#     assert total_points == 20  # 80 - 60 = 20
