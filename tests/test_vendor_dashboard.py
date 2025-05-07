from datetime import datetime, timedelta, timezone

from app.models import Inventory
from app.views.vendor_dashboard import get_user_products


# === Unit Test: Fetch Products for Valid User ===
def test_get_user_products_valid_user(db_session, fake_user):
    """
    Positive test case:
    Scenario: A valid user has multiple products in inventory.
    Expected:
    - The function should return all products tied to that user's ID.
    - Product details should match what was inserted.
    """
    future_date = datetime.now(timezone.utc) + timedelta(days=3)

    # Step 1: Add mock inventory products for the user
    product1 = Inventory(
        name="Product A", user_id=fake_user.id, units=10,
        marked_price=20.0, expiry_date=future_date,
        category="default_category", final_price=10.0, location="Store B"
    )
    product2 = Inventory(
        name="Product B", user_id=fake_user.id, units=5,
        marked_price=15.0, expiry_date=future_date,
        category="default_category", final_price=10.0, location="Store B"
    )
    db_session.add_all([product1, product2])
    db_session.commit()

    # Step 2: Fetch the products using the view helper
    products = get_user_products(fake_user.id)

    # Step 3: Assertions
    assert len(products) == 2
    assert products[0].name == "Product A"
    assert products[1].name == "Product B"


# === Unit Test: No Products for User ===
# def test_get_user_products_no_products(db_session, fake_user):
#     """
#     Negative test case:
#     Scenario: A valid user has no products in the inventory.
#     Expected:
#     - The function should return an empty list.
#     """
#     # Query the helper for a user with no products
#     products = get_user_products(fake_user.id)
#     assert len(products) == 0  # Expect no products
