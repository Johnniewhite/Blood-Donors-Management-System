# Import the necessary libraries
import csv
import urllib.parse
from flask import Flask, render_template, url_for, request, jsonify, redirect
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from dateutil.relativedelta import relativedelta

# Create the Flask app
app = Flask(__name__)

# Read the CSV file into a Pandas DataFrame
data = pd.read_csv("blood_donors.csv")




import datetime

# Define a function to update the Next_Appointment_Date column
def update_next_appointment_dates():
    # Read the CSV file into a Pandas DataFrame
    data = pd.read_csv('blood_donors.csv')

    # Convert the Last_Appointment_Date column to datetime objects
    data['Last_Appointment_Date'] = pd.to_datetime(data['Last_Appointment_Date'], format='%Y-%m-%d')

    # Get the current month and year
    now = datetime.datetime.now()
    current_month = now.month
    current_year = now.year

    # Iterate over the rows of the dataframe
    for index, row in data.iterrows():
        # Get the last appointment date and frequency (in months) for the current row
        last_appointment_date = row['Last_Appointment_Date']
        frequency = row['Frequency(months)']

        # Calculate the next appointment date by adding the frequency to the last appointment date
        next_appointment_date = last_appointment_date + relativedelta(months=frequency)

        # If the Next_Appointment_Date column is empty or contains NaN values, set the next appointment date to the default value
        if pd.isnull(row['Next_Appointment_Date']):
            next_appointment_date = last_appointment_date

        # Get the month and year of the next appointment date
        next_appointment_month = next_appointment_date.month
        next_appointment_year = next_appointment_date.year

        # If the next appointment date is in the past, add the frequency to the next appointment date until it is in the future
        while current_year > next_appointment_year or (current_year == next_appointment_year and current_month > next_appointment_month):
            next_appointment_date = next_appointment_date + relativedelta(months=frequency)
            next_appointment_month = next_appointment_date.month
            next_appointment_year = next_appointment_date.year

        # Update the Next_Appointment_Date column with the next appointment date
        data.loc[index, 'Next_Appointment_Date'] = next_appointment_date

    # Write the updated dataframe to the CSV file
    data.to_csv('blood_donors.csv', index=False)
    return data


def generate_pie_chart():
    # Get the counts of each blood group
    blood_group_counts = data['Blood_Group'].value_counts()

    # Get the labels and values for the pie chart
    labels = blood_group_counts.index
    values = blood_group_counts.values

    # Create the pie chart using matplotlib
    plt.pie(values, labels=labels, autopct='%1.1f%%')
    plt.axis('equal')

    # Save the chart to a file
    plt.savefig('static/images/blood_group_piechart.png', transparent=True)
    plt.close()
def lga_bar():
    # Get the counts of each LGA in the data frame
    lga_counts = data['LGA'].value_counts()

    # Get the labels and values for the bar chart
    labels = lga_counts.index
    values = lga_counts.values

    # Create the bar chart using matplotlib
    plt.bar(labels, values)
    plt.xlabel('LGA')
    plt.ylabel('Count')
    plt.title('Count of Donors by LGA')

    # Save the chart to a file with no background
    plt.savefig('static/images/lga_bar_chart.png', transparent=True)
    plt.close()

def generate_table():
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv('blood_donors.csv')
    df = data.dropna(subset=['Name', 'Sex', 'Date_Of_Birth(d/m/y)', 'LGA', 'Genotype', 'Blood_Group', 'Frequency(months)', 'Phone_number', 'Email_address'])

    html_table = df.head(10).to_html()
    full_table = df.to_html()

    # Generate the bar chart
    lga_bar()
    generate_pie_chart()
    update_next_appointment_dates()


    # Return the HTML table
    return html_table, full_table



import csv
import datetime
from twilio.rest import Client

# Your Account SID and Auth Token from twilio.com/console
account_sid = 'AC98dafde89ff1d30a96c0bcf627032271'
auth_token = '4fa296365da68ab40f327afee49280f8'

# Create a Twilio client
client = Client(account_sid, auth_token)

# Read the CSV file into a Pandas DataFrame
data = pd.read_csv('blood_donors.csv')

# Convert the Next_Appointment_Date column to datetime objects
data['Next_Appointment_Date'] = pd.to_datetime(data['Next_Appointment_Date'], format= '%Y-%m-%d')

# Define a function to send an SMS to a donor 3 days before their next donation date
def send_reminder_sms(row):
    # Get the next appointment date, phone number, and name for the donor
    next_appointment_date = row['Next_Appointment_Date']
    phone_number = row['Phone_number']
    name = row['Name']

    # Calculate the date 3 days before the next appointment date
    reminder_date = next_appointment_date - datetime.timedelta(days=3)

    # Check if the current date is 3 days before the next appointment date
    if datetime.datetime.now() >= reminder_date:
        # Send an SMS message to the donor
        client.messages.create(
            to="+" + str(phone_number),
            from_='+12677442348',
            body=f'Dear {name}, your next donation date is {next_appointment_date:%d/%m/%Y}. kindly endeavour to come and donate. Keep saving lives!'
        )

# Iterate over the rows of the dataframe and send reminder SMS messages to the donors
for index, row in data.iterrows():
    send_reminder_sms(row)
import csv
import datetime
from twilio.rest import Client

# Your Account SID and Auth Token from twilio.com/console
account_sid = 'AC98dafde89ff1d30a96c0bcf627032271'
auth_token = '4fa296365da68ab40f327afee49280f8'

# Create a Twilio client
client = Client(account_sid, auth_token)

# Read the CSV file into a Pandas DataFrame
data = pd.read_csv('blood_donors.csv')

# Convert the Next_Appointment_Date column to datetime objects
data['Next_Appointment_Date'] = pd.to_datetime(data['Next_Appointment_Date'])

# Define a function to send an SMS to a donor 3 days before their next donation date
def send_reminder_sms(row):
    # Get the next appointment date, phone number, and name for the donor
    next_appointment_date = row['Next_Appointment_Date']
    phone_number = row['Phone_number']
    name = row['Name']

    # If the next appointment date is NaT, set it to the current date
    if pd.isnull(next_appointment_date):
        next_appointment_date = datetime.datetime.now()

    # Calculate the date 3 days before the next appointment date
    reminder_date = next_appointment_date - datetime.timedelta(days=3)

    # Check if the current date is 3 days before the next appointment date
    if datetime.datetime.now() >= reminder_date:
        # Send an SMS message to the donor
        client.messages.create(
            to="+" + str(phone_number),
            from_='+12677442348',
            body=f'Dear {name}, your next donation date is {next_appointment_date:%d/%m/%Y}. kindly endeavour to come and donate. Keep saving lives!'
        )

# Iterate over the rows of the dataframe and send reminder SMS messages to the donors
for index, row in data.iterrows():
    send_reminder_sms(row)




# Define the route for the webpage


@app.route('/')
@app.route('/home')
def home():
    html_table, _ = generate_table()
    return render_template('home.html', table=html_table)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route('/stats')
def stats():
    return render_template('stats.html', title='Statistics')


@app.route('/add_entry', methods=['POST', 'GET'])
def add_entry():
    # If the request method is GET, render the form template
    if request.method == 'GET':
        return render_template('add_entry.html')
    # If the request method is POST, handle the form submission
    elif request.method == 'POST':
        # Get the data from the form
        name = request.form['Name']
        sex = request.form['Sex']
        dob = request.form['Date_Of_Birth(d/m/y)']
        lga = request.form['LGA']
        genotype = request.form['Genotype']
        blood_group = request.form['Blood_Group']
        frequency = request.form['Frequency(months)']
        phone_number = request.form['phone_number']
        email = request.form['Email_address']

        # Write the data to the CSV file
        with open('blood_donors.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([name, sex, dob, lga, genotype,
                            blood_group, frequency, phone_number, email])
        # Redirect the user back to the home page
        return redirect(url_for('home'))


@app.route('/table')
def table():
    # Sort the DataFrame by the Name column
    df = data.sort_values(by='Name')
    html_table = df.to_html()
    return render_template('table.html', title='List of Donors', table=html_table)


@app.route('/table/search/', methods=['GET', 'POST'])
def search():
    # Check the request method
    if request.method == 'POST':
        # Get the search query and column name from the form submission
        search_query = request.form['search_query']
        column_name = request.form['column_name']
    elif request.method == 'GET':
        # Get the search query and column name from the URL query string
        search_query = request.args.get('search_query')
        column_name = request.args.get('column_name')
    
    # Set the default column name to Name if no column name is specified
    if not column_name or not column_name.strip():
        column_name = 'Name'
    
    # Check if the search query is not None or an empty string
    if search_query and search_query.strip():
        # Use the search query and column name to filter the data frame
        df = data[data[column_name].str.contains(search_query, case=False, na=False)]
        html_table = df.to_html()

        # Create a list of dictionaries from the data frame
        search_results = []
        for _, row in df.iterrows():
            search_results.append({
                'Name': row['Name'],
                'Sex': row['Sex'],
                'Date_Of_Birth': row['Date_Of_Birth(d/m/y)'],
                'LGA': row['LGA'],
                'Genotype': row['Genotype'],
                'Blood_Group': row['Blood_Group'],
                'Frequency': row['Frequency(months)'],
                'Phone_Number': row['Phone_number'],
                'Email_Address': row['Email_address']
            })

        return render_template('table.html', title='Search Results', table=html_table, search_results=search_results)
    else:
        # Render the table template with an empty search results list
        html_table, _ = generate_table()
        return render_template('table.html', title='Search Results', table=html_table, search_results=[])


@app.route('/table/all', methods=['POST'])
def tabili_all_post():
    # Handle the POST request
    return render_template('table.html')


@app.route('/table/search/<query>', methods=['POST'])
def tabili(query):
    # Retrieve the query parameter from the request body
    query = request.form['query']
    df = data[data['Name'].str.contains(query, case=False)]
    search_results = df.to_dict(orient='records')
    return jsonify(search_results)


if __name__ == '__main__':
    app.run(debug=True)
