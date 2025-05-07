# Green Campus

## 🌎 Project Overview

**Green Campus** is a sustainability management platform for university
campuses, tackling greenhouse gas emissions, resource waste, and
inefficient energy use. It provides real-time tools to monitor and
promote eco-friendly initiatives, engaging students and staff with
actionable insights. Using IoT sensors, it tracks energy consumption and
waste management, offering a smart energy dashboard, a gamified
Eco-Points system, and a food waste reduction feature through dynamic
discounts. By combining real-time monitoring, gamification, and user
engagement, Green Campus fosters sustainable behaviors, positioning
itself as a model for eco-friendly campus operations worldwide. (Word
count: 94)

## Setup

1.  **Clone the Repository**\
    Clone the project repository to your local machine:

    ``` bash
    git clone https://github.com/radhikari-3/green-campus.git
    cd green-campus
    ```

2.  **Install Dependencies**\
    Install the required dependencies using pip:

    ``` bash
    pip install -r requirements.txt
    ```

3.  **Setup Docker**\
    Ensure Docker is installed and running. Run the Docker Compose file:

    ``` bash
    docker compose up
    ```

4.  **Initialize the Database**\
    Run the following commands to create the database:

    ``` bash
    flask shell
    >>> db.create_all()
    ```

5.  **Run Tests**\
    Execute the test suite to ensure functionality:

    ``` bash
    pytest
    ```

6.  **Access the Application**\
    Open your browser and navigate to `http://localhost:5000`.

## Technologies Used

-   **Programming Languages**: Python, HTML
-   **Frameworks**: Flask (backend), Charts.js, Plotly (frontend)
-   **Tools**: Docker, PostgreSQL, Pytest (testing), Git (version control)
-   **Libraries**: SQLAlchemy (ORM), Chart.js (data visualization),
    qrcode (QR code generation), Bootstrap (UI components), Flask-Mail, Flask-Scheduler, Flask-Login

## Implemented Functionalities
1.  **Smart Campus Energy Dashboard**
    -   Displays [real-time energy usage](http://127.0.0.1:5000/energy_analytics) and environmental impact metrics 
    (e.g., Energy Use per Building, Zone wise Energy use per building, CO2 emissions).
    -   Visualizes consumption patterns with interactive charts.
2.  **Gamified Eco-Points and Rewards System**
    -   [Track Eco-Points](http://127.0.0.1:5000/dashboard) awarded for sustainable actions (e.g., cycling,
        walking) to promote eco-friendly behavior.
    -   Allows [point redemption](http://127.0.0.1:5000/rewards) using QR code vouchers at campus vendors to reduce food waste.
3.  **Smart Expiring Food Discount System**
    -   Enables students to [view and purchase near-expiry food items](http://127.0.0.1:5000/view_expiring_products) 
    at discounted prices.
    - [Filters products](http://127.0.0.1:5000/expiring-offers/f) based on user preferences (e.g., price, expiry, location).
4. **Vendor Smart Expiry System**
    -   Enables vendors to [list near-expiry food items](http://127.0.0.1:5000/smart_food_expiry) with dynamic
        discounts so that students can purchase them at a lower price.
    -   Sends daily email notifications to users about available
       discounts on products, encouraging them to buy before expiry.
5.  **User Authentication and Authorization**
    -   Implements user authentication and authorization using Flask-Login, Flask-Mail.
    -   Allows users to [register](http://127.0.0.1:5000/auth/signup), [log in](http://127.0.0.1:5000/auth/login) using email, password, and OTP.
    -   Provides password reset functionality via email.

    
Note: The URLs provided in the functionalities section are local links and may not work outside the local environment. 
Run the application locally to access them.

## System Architecture

### Design Patterns
-   **Model-View-Controller (MVC)**: Separates data, user interface,
    and control logic for better organization and maintainability.
-   **Publish-Subscribe**: pattern for real-time notifications and updates.
-   **Singleton**: Ensures a single instance of the database connection
    throughout the application.

### Class Relationships


### Simulated API/IoT Sensor Data
-   **Energy Usage**: Simulated data from IoT sensors for real-time
    energy consumption.
-   **Eco-Points**: Points awarded based on user actions, stored in
    the database.
-   **Food Discounts**: Vendor-submitted data for near-expiry items
    with dynamic discounts.

### CI/CD Pipeline
GitHub Actions automates the CI/CD pipeline, triggered on every push or pull request (PR) to the main branch. 
The workflow includes:

- **Linting**: Flake8 checks Python code for style and quality issues.
- **Testing**: Pytest runs the test suite to verify functionality.
- **Build Quality**: Docker builds the application container to ensure deployment readiness.
- **Security Checks**: Dependabot scans for vulnerabilities in dependencies.
- **PR Review Process**: Each PR undergoes peer review, requiring approval and passing CI checks (build status, tests, security scans) before merging.
- **Pipeline Configuration**: Defined in `.github/workflows/ci.yml`, ensuring code quality, security, and reliable deployments.

## Test Cases

| **Feature**                        | **Test Case**                                | **Scenario**                                                                 | **Status**       |
|------------------------------------|----------------------------------------------|-------------------------------------------------------------------------------|------------------|
| **Smart Campus Energy Dashboard**  | `test_get_building_names`                    | Mock database query to fetch building names.                                 | ✅ Passed        |
|                                    | `test_get_energy_usage_by_zone`              | Mock database query to fetch energy usage by zone.                           | ✅ Passed        |
|                                    | `test_energy_dashboard_view`                 | Verify energy dashboard page loads successfully.                             | ✅ Passed        |
|                                    | `test_get_line_chart_view_invalid_payload`   | Test invalid payload for line chart view.                                    | ✅ Passed        |
|                                    | `test_get_energy_usage_by_zone_invalid_data` | Handle invalid energy usage data gracefully.                                 | ✅ Passed        |
|                                    | `test_get_building_names_empty`              | Handle empty building names gracefully.                                      | ✅ Passed        |
|                                    | `test_get_energy_usage_by_zone_empty`        | Handle empty energy usage data gracefully.                                   | ✅ Passed        |
| **Gamified Eco-Points System**     | `test_calculate_total_eco_points`            | Calculate total eco-points for a user.                                       | ✅ Passed        |
|                                    | `test_calculate_user_eco_points_valid_user`  | Calculate eco-points for a valid user.                                       | ✅ Passed        |
|                                    | `test_calculate_user_eco_points_no_points`   | Handle scenario where user has no eco-points.                                | ✅ Passed        |
| **Authentication**                 | `test_login_with_unverified_email`           | Test login with an unverified email.                                         | ✅ Passed        |
| **Vendor Dashboard**               | `test_get_user_products_valid_user`          | Fetch products for a valid user.                                             | ✅ Passed        |
|                                    | `test_get_user_products_no_products`         | Handle scenario where user has no products.                                  | ✅ Passed       |

