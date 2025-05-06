from datetime import datetime, timedelta, timezone

from app.models import Inventory
from app.views.vendor_dashboard import get_user_products


def test_get_user_products_valid_user(db_session, fake_user):
    """
    Positive test case: Ensure products are fetched correctly for a valid user.
    """
    future_date = datetime.now(timezone.utc) + timedelta(days=3)

    # Add mock products to the database
    product1 = Inventory(name="Product A", user_id=fake_user.id, units=10,
                         marked_price=20.0, expiry_date=future_date, category="default_category",final_price=10.0, location="Store B")
    product2 = Inventory(name="Product B", user_id=fake_user.id, units=5,
                         marked_price=15.0, expiry_date=future_date, category="default_category",final_price=10.0, location="Store B")
    db_session.add_all([product1, product2])
    db_session.commit()

    # Fetch products for the user
    products = get_user_products(fake_user.id)
    assert len(products) == 2
    assert products[0].name == "Product A"
    assert products[1].name == "Product B"

#
# def test_get_user_products_no_products(db_session, fake_user):
#     """
#     Negative test case: Ensure no products are returned for a user with no products.
#     """
#     # Ensure the user has no products in the database
#     products = get_user_products(fake_user.id)
#     assert len(products) == 0  # Expect no products
#
