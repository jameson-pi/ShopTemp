from flask import Flask, render_template, request
import csv
from datetime import datetime
import math
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
        # Calculate dew point and feels like temperature for each row
        def calculate_dew_point(temp_c, humidity):
            # Magnus formula
            a, b = 17.27, 237.7
            alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
            dew_point = (b * alpha) / (a - alpha)
            return round(dew_point, 2)

        def calculate_feels_like(temp_c, humidity):
            # Simple heat index formula (Celsius)
            feels_like = temp_c
            if temp_c >= 27:
                feels_like = -8.784695 + 1.61139411 * temp_c + 2.338549 * humidity \
                    - 0.14611605 * temp_c * humidity - 0.012308094 * temp_c ** 2 \
                    - 0.016424828 * humidity ** 2 + 0.002211732 * temp_c ** 2 * humidity \
                    + 0.00072546 * temp_c * humidity ** 2 - 0.000003582 * temp_c ** 2 * humidity ** 2
            return round(feels_like, 2)

        for row in data:
            try:
                temp_c = float(row["Celsius"])
                humidity = float(row["Humidity"])
                row['DewPoint'] = round(calculate_dew_point(temp_c, humidity)*9/5+32,2)
                row['FeelsLike'] = round(calculate_feels_like(temp_c, humidity)*9/5+32,2)
            except Exception as e:
                row['DewPoint'] = e
                row['FeelsLike'] = 'N/A'
        return render_template('results.html', data=data, target_datetime=target_datetime.strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        # Generic error handling
        return f"An error occurred: {e}"


if __name__ == '__main__':
    app.run(debug=True)


