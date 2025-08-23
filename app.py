from flask import Flask, render_template, request
import csv
from datetime import datetime

app = Flask(__name__)

# Function to filter data from CSV

# The user's prompt seems to be correcting the logic within the existing functions
# based on the new CSV file details. The placeholder is oddly placed,
# but the intent is to fix the code to work with the specified CSV.
# The following code replaces the entire filter_csv_data function and updates the search function.

def filter_csv_data(file_path, target_datetime):
    """
    Filters data from a CSV file to find rows that match the target date and time,
    ignoring microseconds.
    """
    filtered_data = []
    try:
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    # Parse timestamp from the 'Timestamp' column
                    row_datetime = datetime.strptime(row['Timestamp'], '%Y-%m-%dT%H:%M:%S.%f')
                    # Compare with target_datetime, ignoring microseconds for the match
                    if row_datetime.replace(second=0,microsecond=0) == target_datetime.replace(year=2024,minute=(round(target_datetime.minute/10)*10),second=0,microsecond=0):
                        filtered_data.append(row)
                except (ValueError, KeyError):
                    # Skip rows with parsing errors or missing 'Timestamp' key
                    continue
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    return filtered_data

@app.route('/search')
def index():
    return render_template('index.html')

@app.route('/', methods=['GET'])
def search():
    try:
        # Get the current time and remove microseconds for comparison
        target_datetime = datetime.now().replace(microsecond=0)
        # Use the correct CSV file name
        file_path = 'trashed-1758328976-CurrentTempLog.csv'
        data = filter_csv_data(file_path, target_datetime)
        return render_template('results.html', data=data, target_datetime=target_datetime.strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        # Generic error handling
        return f"An error occurred: {e}"


if __name__ == '__main__':
    app.run(debug=True)


