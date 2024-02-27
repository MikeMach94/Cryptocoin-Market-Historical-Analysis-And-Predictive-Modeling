# Cryptocoin Market Historical Analysis And Predictive Modeling
## Description

This project is a comprehensive endeavor aimed at contributing to the ongoing research of cryptocurrency historical analysis. By evaluating the impact of major historical, economic, and geopolitical developments on the cryptocurrency market, we seek to provide valuable insights into the behavior and trends of various cryptocurrencies. Through meticulous analysis and comparison of price trends, we aim to uncover patterns and correlations that can aid in understanding market dynamics.

**Assignee** : A consulting firm that aims to provide an investment plan consisting of advice, guidance, and strategic insights for crypto coin market, also any individual who is actively involved in crypto coin trading for personal benefit.

**Purpose** : Analyze the influence of historical, economic, and geopolitical factors on cryptocurrency markets and develop predictive models to forecast prices, aiding decision-making for investors and researchers.

**Problem** : Insufficient availability of well-organized historical economic data on crypto coins that align with the analysis criteria.

**Solution** : The creation of a database that consists of data needed for their analysis and visualization.

## Prerequisites:

* Data collection has to be an automated ETL process.

* Data have to be available to analysts and researchers in a specific, given form.

* Ability to visualize data in the form of questions.

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

## How to install
