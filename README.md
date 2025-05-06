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

-   **Programming Languages**: Python, JavaScript, HTML, CSS
-   **Frameworks**: Flask (backend), Charts.js, Plotly (frontend)
-   **Tools**: Docker, PostgreSQL, Ioiotron (IoT sensor integration),
    Pytest (testing), Git (version control)
-   **Libraries**: SQLAlchemy (ORM), Chart.js (data visualization),
    qrcode (QR code generation)

## Implemented Functionalities

1.  **Smart Campus Energy Dashboard**
    -   Displays real-time energy usage and environmental impact metrics
        (e.g., CO2 emissions).\
    -   Visualizes consumption patterns with interactive charts.
2.  **Gamified Eco-Points and Rewards System**
    -   Awards Eco-Points for sustainable actions (e.g., recycling,
        walking).\
    -   Allows point redemption for QR code vouchers at campus vendors.
3.  **Smart Expiring Food Discount System**
    -   Enables vendors to list near-expiry food items with dynamic
        discounts.\
    -   Sends real-time notifications to users about available
        discounts.

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

### 1. Smart Campus Energy Dashboard

-   **Positive Test Case**:
    -   **Scenario**: User views real-time energy usage.
    -   **Steps**: Log in, navigate to dashboard, verify energy usage
        data (e.g., kWh) and CO2 metrics display correctly.
    -   **Expected Result**: Data is accurate, charts render without
        errors.
-   **Negative Test Case**:
    -   **Scenario**: IoT sensor data is unavailable.
    -   **Steps**: Simulate sensor failure, access dashboard.
    -   **Expected Result**: Graceful error message displayed, dashboard
        remains functional.

### 2. Gamified Eco-Points and Rewards System

-   **Positive Test Case**:
    -   **Scenario**: User earns and redeems Eco-Points.
    -   **Steps**: Perform sustainable action (e.g., log recycling),
        check points balance, redeem points for a QR voucher.
    -   **Expected Result**: Points updated, QR code generated and
        valid.
-   **Negative Test Case**:
    -   **Scenario**: User attempts to redeem points with insufficient
        balance.
    -   **Steps**: Attempt redemption with 0 points.
    -   **Expected Result**: Error message indicating insufficient
        points.

### 3. Smart Expiring Food Discount System

-   **Positive Test Case**:
    -   **Scenario**: Vendor lists near-expiry item, user receives
        notification.
    -   **Steps**: Vendor adds item with discount, user checks
        notifications.
    -   **Expected Result**: Notification received, item listed with
        correct discount.
-   **Negative Test Case**:
    -   **Scenario**: Vendor submits invalid expiry date.
    -   **Steps**: Vendor enters future date beyond threshold (e.g., 1
        year).
    -   **Expected Result**: Form validation fails, error message
        displayed.

