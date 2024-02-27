# Cryptocoin Market Historical Analysis And Predictive Modeling

## Description

This project is a comprehensive endeavor aimed at contributing to ongoing research in cryptocurrency historical analysis. By evaluating the impact of major historical, economic, and geopolitical developments on the cryptocurrency market, we seek to provide valuable insights into the behavior and trends of various cryptocurrencies. Through meticulous analysis and comparison of price trends, we aim to uncover patterns and correlations that can aid in understanding market dynamics.

### Assignee

This project targets a consulting firm aiming to provide an investment plan consisting of advice, guidance, and strategic insights for the crypto coin market. Additionally, it caters to individuals actively involved in crypto coin trading for personal benefit.

### Purpose

The primary objective is to analyze the influence of historical, economic, and geopolitical factors on cryptocurrency markets. This analysis will contribute to developing predictive models to forecast prices, aiding decision-making for investors and researchers.

### Problem

The project addresses the challenge of insufficient availability of well-organized historical economic data on crypto coins that align with the analysis criteria.

### Solution

The proposed solution involves the creation of a database consisting of data required for analysis and visualization.

## Prerequisites

- Data collection must be automated through an ETL process.
- Data must be available to analysts and researchers in a specific, standardized format.
- Visualization of data should facilitate posing and answering questions.

## Solution Approach

* Appropriate data collection out of a reliable source.
  
* Structure the implementation plan.
  
* Choose the tools that will be used.

**1) Source of data** 

APIs used:

base_url = 'https://api.binance.com'

endpoint = '/api/v3/klines'

**2) Implementation plan.** 

* Build a database to store data.

* Create a script that will call the APIs, fetch data, manipulate and transform data to meet the assignee’s criteria and store them into the database.

* Use specific tools to make the process automated and fail-proof.

**3) Tools used.**

![Screenshot 2024-02-27 145637](https://github.com/MikeMach94/Cryptocoin-Market-Historical-Analysis-And-Predictive-Modeling/assets/125815367/17572230-969c-4bd3-b74c-7a7232cda5cb)

## Airflow DAG Pipeline Description

The Airflow DAG is scheduled to run every day at 00:30.

### Steps of Execution:

1. **Check Database Connection (`check_database_connection`):** Airflow initiates by verifying the availability of the database. If the database is offline, the process halts, and a notification is logged regarding the incident.

2. **Check API Connectivity (`test_binance_connectivity`):** Following a successful database connection, Airflow proceeds to verify the availability and data serving capability of the API. If the API is inaccessible, the process halts, and a notification is logged.

3. **Check Database Status (`check_if_database_empty`):** After confirming both database and API availability, Airflow evaluates if the database is empty. Utilizing the `BranchPythonOperator`, the workflow diverges based on the database status.

    - If the database is empty:
        - **Populate Database (`populate_database_task`):** This task populates the database with data ranging from 2017 to the current date. It triggers when the process runs for the first time or when a database switch occurs.

    - If the database is not empty:
        - **Extract Latest Timestamp (`extract_latest_timestamp`):** In this branch, the task retrieves the latest timestamp from the last database entry using `Xcom`.

4. **Add Latest Data (`add_the_latest_data_task`):** Finally, leveraging the latest timestamp obtained from `Xcom` as a starting point, this task fills the database with missing data up to the current date.

![Screenshot 2024-02-27 150548](https://github.com/MikeMach94/Cryptocoin-Market-Historical-Analysis-And-Predictive-Modeling/assets/125815367/7150020d-2a8d-4650-9c7c-2bf8bd0a2592)

As a result the database is filled with the data necessary for the research.

## pgAdmin GUI + PostgreSQL Database

![Screenshot 2024-02-25 165803](https://github.com/MikeMach94/Cryptocoin-Market-Historical-Analysis-And-Predictive-Modeling/assets/125815367/be53a3bf-4abe-4e4d-b5a4-22356a324066)

## About Our Data

* 10 Crypto Coins
* 2 Currencies
* 1 Day Intervals
* Daily Data Update
* Data Range (2017-Current Date)
* Open/Close Time
* Open/Close Price
* Trade Volume
* Trade Count 

Then we connect metabase to the database. That way data can be visualized.

![Screenshot 2024-02-25 165951](https://github.com/MikeMach94/Cryptocoin-Market-Historical-Analysis-And-Predictive-Modeling/assets/125815367/b1695f9a-c9f9-4716-a134-98175a8612ee)

![Screenshot 2024-02-25 170002](https://github.com/MikeMach94/Cryptocoin-Market-Historical-Analysis-And-Predictive-Modeling/assets/125815367/cb0651ef-b5c8-4cf9-b1b0-11ef588c4680)

## How to Install

To set up this project on Ubuntu 22.04.3 LTS with Docker version 25.0.1 and Docker-compose version 1.29.2, follow these steps:

1. **Clone the Repository:**
   Copy the contents of this repository to your local machine.

2. **Create a DockerHub Account:**
   If you haven't already, create an account on DockerHub, which serves as the Docker image repository.

3. **Set Up PostgresDB and pgAdmin:**
   - Navigate to the `PostgresDB_pgAdmin` folder.
   - Edit the `postgres.env` file to include your credentials.
   - Run `docker-compose up -d` to create a Docker container with PostgresDB and a pgAdmin GUI.
     You can customize the `docker-compose.yml` file according to your preferences.

4. **Deploy Airflow:**
   - Go to the `Airflow` folder.
   - Execute `docker-compose up -d` to create all necessary containers for Airflow.
     The DAG and essential project files are already included.
   - Customize settings such as database name, host machine IP, and credentials in the config file found in the main branch and the `Airflow` folder.

5. **Launch Metabase:**
   - Access the `Metabase` folder.
   - Run `docker-compose up -d`.
   - Connect Metabase to the database using your credentials.

6. **Configure Airflow Connections:**
   - In the Airflow GUI, navigate to Admin > Connections.
   - Set up a Postgres connection using the database created earlier. This step is necessary for the PostgresOperator to function properly.

Please note that while this guide provides an overview of the setup process, detailed documentation for each component and step is available within the respective files. For example, the DAG file provides comprehensive documentation regarding its functionality and usage.

For any inquiries or assistance, feel free to contact me via LinkedIn.

## License

You are welcome to utilize any part of this project for your own endeavors. If you find it helpful, I would highly appreciate to mention me using my linkedin profile.
