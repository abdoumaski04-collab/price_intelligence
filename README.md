# MobilierPrix - Price Intelligence Platform

This project is an end-to-end data engineering and price intelligence platform designed to aggregate, analyze, and visualize pricing data for furniture across major retailers in Morocco (Jumia, IKEA, and Kitea). The system captures data streams, performs advanced analytics (machine learning, hypothesis testing, anomaly detection), and presents the findings through a robust, fullstack web application.

The platform was built through the collaboration of five distinct technical roles. Below is a breakdown of the architecture and the contributions of each role.

---

### 1. DataOps
- **Infrastructure Orchestration:** Set up and maintained the foundational architecture using Docker Compose, integrating services like Zookeeper, Kafka, Apache NiFi, and Apache Airflow.
- **Workflow Automation:** Ensured seamless scheduling and monitoring of data pipelines via Airflow.
- **System Reliability:** Managed container lifecycles, health checks, and logging to guarantee high availability for continuous data processing.

### 2. Data Engineer
- **Data Ingestion:** Designed complex ingestion flows using Apache NiFi to scrape and gather raw data from multiple ecommerce sources (Jumia, IKEA, Kitea).
- **Streaming & Messaging:** Configured Kafka topics to handle high-throughput data streams efficiently.
- **Data Warehousing & Transformation:** Integrated Google Cloud Platform (GCP) services, storing massive datasets in Bigtable and BigQuery. Utilized `dbt` (Data Build Tool) within the Airflow pipelines to clean, model, and transform raw data into analytical tables.

### 3. Data Analyst
- **Statistical Analysis:** Conducted rigorous hypothesis testing (Kruskal-Wallis, Mann-Whitney, Shapiro-Wilk) to compare pricing strategies across the three retailers.
- **Machine Learning:** Built predictive models (Random Forest, clustering) to determine feature importance, predict prices, and segment products into distinct categories.
- **Insights Generation:** Computed promotional rates, price velocities, and confidence intervals, exporting these critical insights into structured JSON assets (`analyse_results.json`, `fig_*.json`) for downstream consumption.

### 4. DevSecOps
- **Security Configuration:** Secured the infrastructure by enforcing authentication on NiFi and Airflow instances. 
- **Credential Management:** Handled secure injection of GCP service account keys (`gcp-key.json`) and environment variables (`.env`).
- **Network Security:** Configured secure CORS policies in the backend API to strictly allow traffic from authorized frontend origins, preventing cross-site request forgery.

### 5. Fullstack Engineer (Primary Focus)
The Fullstack Engineer bridged the gap between raw data and end-user experience, building a high-performance web application consisting of a FastAPI backend and an Angular frontend.

**Backend (Python / FastAPI):**
- Built `data_analy/api/main.py`, a high-performance REST API handling asynchronous requests.
- Implemented robust data querying logic capable of switching seamlessly between Google BigQuery, Google Bigtable, and local CSV fallbacks (`DATA_MODE`).
- Created complex search and filtering endpoints (`/search`) supporting pagination, price bounding, and sorting.
- Exposed analytical endpoints (`/stats`, `/promotions`, `/velocity`, `/figure/{nom}`) to serve the pre-computed machine learning models and Plotly configurations directly to the frontend.
- Implemented request audit logging via custom FastAPI middleware.

**Frontend (Angular / TypeScript):**
- Developed a modern, component-based architecture using Angular Standalone Components and the new Signals API for reactive state management.
- **UI/UX Design:** Designed a premium, glassmorphism-inspired interface with a cohesive color palette (Off-white background, Brown primary accents, Black typography). Ensured all hover states and transitions were smooth and accessible.
- **Data Dashboard:** Integrated `Plotly.js` to render complex interactive charts (KDE density plots, Boxplots, Scatter plots, ML Feature Importance) dynamically fetched from the backend.
- **Routing & Authentication Flow:** Configured Angular Router to handle navigation between the public search interface, a secure gateway login page (`/analytics-access`), and the protected analytics dashboard (`/dashboard`).
- **Search & Pagination:** Built a responsive product grid with dynamic server-side filtering, allowing users to cross-reference prices between Jumia, IKEA, and Kitea instantly.
