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

## Usage

Airflow DAG is scheduled to run everyday at 00:30.

Steps of execution:

1. Airflow checks if the database is online (check_database_connection). If not, the process stops and we get a notification for the incident in Logging.

If the DB is online,

2. Airflow checks if the API is online and serves data (test_binance_connectivity). If not, the process stops and we get a notification for the incident in Logging.

If the API is online and serves data, 

3. Airflow checks if the database is empty (check_if_database_empty) and using BranchPythonOperator leads the workflow to the appropriate route.


