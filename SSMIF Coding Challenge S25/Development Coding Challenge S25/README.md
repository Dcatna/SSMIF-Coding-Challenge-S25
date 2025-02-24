This project was created by Dominic Catena for SSMIF 2025 Coding Challenge, 
github url: https://github.com/Dcatna/SSMIF-Coding-Challenge-S25/tree/main/SSMIF%20Coding%20Challenge%20S25/Development%20Coding%20Challenge%20S25.

Tech Stack:
    - Typescript
    - React
    - Shadcn
    - Zustand
    - recharts
    - Supabase
    - Tailwind
    - Python
    - Pandas
    - CORS

This project displays the Portfolio Sector Performance, Portfolio Value alone and against the S&P500, current holdings (ticker, quantity, day and total change, market value,
unit cost, total cost) and a table for all of the trades starting from 2015-01-01 - 2024-12-01.

**To run this project you need to cd to the frontend folder and run npm install to install all dependencies, then in a seperate terminal (for ease) cd to the backend and install all of the dependencies from flask, flask_cors, pandas, yfinance, supabase, os, dotenv through pip install <flask, ...>**

**To run the frontend go to the frontend folder and run npm run dev and click on the localhost url (I didnt have enough time to deploy this due to having a lot of work to do this week)**
**To run the backend go to the backend folder and run python app.py**

To access the page go to create an account and create your account, it will send you a verification email which you must access before signing in. Once done you will have access to the home page. 

For simplicity I included the supabase public key and url to access the database for the front and backend, which is a Timeseries/PostgreSQL database to support the graphs and a regular PostgreSQL database for user authentication and management.

