## 🌎 Project Overview

**Green Campus** is an innovative sustainability management platform designed for university campuses, addressing major 
challenges such as greenhouse gas emissions, resource waste, and inefficient energy use. Despite existing sustainability efforts, 
many institutions lack comprehensive, real-time tools to monitor and promote eco-friendly initiatives.

Green Campus fills this gap by providing a tech-driven solution that engages both students and staff through meaningful, actionable insights.

The system leverages IoT sensors to monitor real-time energy consumption and waste management across the campus.

### Key Features

1. **Smart Campus Energy Dashboard**
   - Displays real-time resource usage and calculates environmental impact metrics.
   - Provides users with insights into their energy consumption patterns, enabling informed decisions about resource usage.

2. **Gamified Eco-Points and Rewards System**
   - Incentivizes sustainable actions like walking, recycling, and carpooling.
   - Users can redeem their Eco-Points for QR code vouchers at campus establishments.
   - Includes a gamified Eco-Points and Rewards System that incentivizes sustainable actions like walking, recycling, and carpooling.
   - Users can redeem their Eco-Points for QR code vouchers at campus establishments.

3. **Smart Expiring Food Discount System**
   - Enables vendors to register items nearing expiration, helping to reduce food waste through dynamic discounting and real-time notifications.

By combining real-time monitoring, gamification, and user engagement, Green Campus promotes sustainable behaviors and 
drives long-term environmental impact, positioning itself as a model for universities worldwide striving for eco-friendly campus operations.

## Setup

1. **Clone the Repository**  
   Clone the project repository to your local machine:
   ```bash
   git clone https://github.com/radhikari-3/green-campus.git
   cd green-campus
   
2. **Install Dependencies**
   Install the required dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Docker**
   Ensure Docker is installed and running on your system. Run the docker compose file:
   ```bash
   docker compose up
    ```

4. **Initialize the Database**
   On terminal or command prompt, run the following commands to create the database:
   flask shell
   ```bash
   >>> db.create_all()
   ```

5. **Run Tests**
   Execute the test suite to ensure everything is working:
   ```bash
   pytest
   ```
   
6. **Access the Application**
Open your web browser and navigate to `http://localhost:5000` to access the application.
