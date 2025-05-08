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
itself as a model for eco-friendly campus operations worldwide.

## Setup

1.  **Clone the Repository**\
    Clone the project repository to your local machine:

    ``` bash
    git clone https://github.com/radhikari-3/green-campus.git
    cd green-campus
    ```
    

2.  **Install Conda**\
    If you don't have Conda installed, download and install it from 
    the official website: [Anaconda](https://www.anaconda.com/products/distribution).


3.  **Create a Conda Environment**\
    Create a new Conda environment for the project:

    ``` bash
    conda create -n green-campus python=3.12
    ```
    Activate the environment:

    ``` bash
    conda activate green-campus
    ```


4.  **Install Dependencies**\
    Install the required dependencies using pip:

    ``` bash
    pip install -r requirements.txt
    ```


5.  **Setup Docker (Optional)**\
    Ensure Docker is installed and running. Run the Docker Compose file
    presented in the project directory, if you wish to use Docker for PostgreSQL and MQTT services.:

    ``` bash
    docker compose up
    ```
    Note: Make sure to have Docker installed and running on your machine.
    This command will start the PostgreSQL database and other services (MQTT) defined in the `green-campus/docker-compose.yml` file.


6.  **Setup Environment Variables**\
    Change the `.flaskenv` file in the root directory of the project as needed.:

    ```aiignore
        #DB Connection
        DB_USERNAME=<YOUR DB USERNAME>  # Database username for connecting to PostgreSQL.
        DB_PASSWORD=<YOUR DB PASSWORD>  # Database password for the specified username.
        DB_NAME=<YOUR DB NAME>  # Name of the PostgreSQL database.
        
        #Email Service
        SENDGRID_API_KEY = "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"  # API key for SendGrid email service.
        MAIL_DEFAULT_SENDER = 'testinggreencampus@outlook.com'  # Default sender email address for outgoing emails.
        
        #Scheduler and IoT Simulator
        SCHEDULER_ENABLED = False  # Flag to enable or disable the task scheduler which runs at 7 AM daily.
        SCHEDULER_TEST_NOW = False  # Flag to trigger immediate execution of scheduled tasks.
        IOT_SIMULATOR_ACTIVE = False  # Flag to activate or deactivate the IoT simulator.
    ```


7.  **Initialize the Database**\
    Run the following commands to create the database:

    ``` bash
    flask shell
    >>> db.create_all()
    ```


8.  **Initialize the Database**\
    Run the following commands to create the database:

    ``` bash
    flask shell
    >>>    reset_db()
       ```
    Note: This command will create the database tables and populate them with initial data.
    This might take a few minutes, depending on your system's performance.
    

9.  **Create Run Configurations**\
    Create a new run configuration in your IDE (e.g., PyCharm) to run the Flask application.

    ```
    Go to Run > Edit Configurations.  
    Click on the "+" icon to add a new configuration.
    Select "Flask Server" from the list.
    Name the configuration (e.g., "Green Campus").
    In the Run Configuration, set the following:
    Select your Python interpreter (the one where you installed the dependencies).
    Module path: `flask` 
    command: `run`
    Working directory: `<path_to_your_project_directory>`
    Path to ".env" files: `<path_to_your_project_directory>/.flaskenv`
    ```
    

10. **Access the Application**\
    Open your browser and navigate to `http://127.0.0.1:5000`.

## Technologies Used

-   **Programming Languages**: Python, HTML
-   **Frameworks**: Flask (backend), Charts.js, Plotly (frontend)
-   **Tools**: Docker, PostgreSQL, Pytest (testing), Git (version control)
-   **Libraries**: SQLAlchemy (ORM), qrcode (QR code generation), Bootstrap (UI components), 
      Flask-Mail, Flask-Scheduler, Flask-Login

## Test Users
Note : The test users are pre-populated in the database. New users can be created using the signup page, 
but they will not have any eco-points or rewards.

You can use the following test users to log in to the application:

| **Email**                     | **Password** |  **Role**  |
|-------------------------------|--------------|------------|
|   tom.b12345@yopmail.com      | amy.pw       | Normal     |
|   yin.b12345@yopmail.com      | amy.pw       | Normal     |
|   jo.b12345@yopmail.com       | amy.pw       | Normal     |

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
-   **Publish-Subscribe**: Pattern for real-time notifications of IoT sensor data and updates.
-   **Singleton**: Ensures a single instance of the database session
    throughout the application.

### Class Relationships
 
1. **Inheritance**
    Inheritance allows a model to inherit properties and behaviors from parent classes.
    ```python
    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(120), unique=True)
    ```
    Description: User inherits from db.Model (SQLAlchemy base for database models) and UserMixin (Flask-Login for authentication).


2. **Association**
    Association represents a loose connection between models, typically via a foreign key.

    ```python
    class ActivityLog(db.Model):
        email = db.Column(db.String(120), db.ForeignKey('users.email'))
        user = db.relationship("User", back_populates="activity_logs")
    ```
    Description: ActivityLog links to User via email. The relationship is loose, meaning ActivityLog can exist 
    independently unless cascading deletes are configured.


3.  **Composition**
    Composition represents strong ownership where the child’s lifecycle is tied to the parent.
    ```python
    class User(UserMixin, db.Model):
        inventory = db.relationship(
            "Inventory", back_populates="user",
            cascade="all, delete-orphan"
        )
    ```
    Description: Deleting a User also deletes their Inventory items due to the cascade="all, delete-orphan" setting.
   
4. **Aggregation**
    Aggregation represents a logical grouping where the child can exist independently.
    ```python
    class Building(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100))
        readings = db.relationship("EnergyReading", backref="building")
    class EnergyReading(db.Model):
        building_id = db.Column(db.Integer, db.ForeignKey("building.id"))
    ```
    Description: EnergyReading is associated with a Building, but can be reassigned or exist independently (no delete cascade).


    A summary table that outlines the relationship types and their descriptions.

   | **Relationship Type** | **Example (from project)** | **Description** |
   |-----------------------|----------------------------|------------------|
   | Inheritance           | User → UserMixin, db.Model | Adds authentication and model behavior |
   | Association           | ActivityLog → User (email) | Loosely linked via foreign key |
   | Composition           | User → Inventory           | Child bound to parent’s lifecycle |
   | Aggregation           | Building → EnergyReading   | Logical grouping; child can exist independently |


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

## Contributing Members
| **Name and Id**       | **Contribution(%)** | **Key Contributions**                                    | 
|-----------------------|---------------------|----------------------------------------------------------|
| Rohit Adhikari (100)  | 20%                 | Contributed extensively to core features <br/>(MQTT, CI pipeline, dashboards, UI, CO2 chart)    |
| Viswanath Nair (101)  | 20%                 | Contributed to vendor management and email functionality |
| Anupama Hasurkar(102) | 20%                 | Added Authentication of Users                            |
| Yash Zore (104)       | 20%                 | Focused on gamification, eco points dashboard, <br/>and UI enhancements, with significant feature additions.                             |
| Melissa Zulle (103)   | 20%                 | Contributed to the smart food expiry feature                    |

