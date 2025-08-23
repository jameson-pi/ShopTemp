from datetime import datetime
from PIL import Image, ImageDraw
import time
import pixoo
import csv
class PixooWeatherDisplay:
    def __init__(self, device_ip, city="Austin"):
        self.pixoo = pixoo.Pixoo(device_ip, simulated=True)
        self.city = city
        self.size = (64, 64)
    def get_high_temp(self, weather_data, date):
        """Extract high temperature from weather data"""
        highf = -100
        for entry in weather_data:
            if datetime.strptime(entry['Timestamp'], '%Y-%m-%dT%H:%M:%S.%f').date() != date.date():
                high_temp = float(entry['Fahrenheit'])
                if high_temp > highf:
                    highf = high_temp
        return highf
    def filter_csv_data(self, file_path, target_datetime):
        filtered_data = []
        highTemp = -100
        try:
            with open(file_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                highTemp = self.get_high_temp(reader, target_datetime)
                print(highTemp)
                for row in reader:
                    try:
                        # Parse timestamp from the 'Timestamp' column
                        row_datetime = datetime.strptime(row['Timestamp'], '%Y-%m-%dT%H:%M:%S.%f')
                        # Compare with target_datetime, ignoring microseconds for the match
                        if row_datetime.replace(second=0,microsecond=0) == target_datetime.replace(year=2024,minute=(round(target_datetime.minute/10)*10),second=0,microsecond=0):
                            filtered_data.append(row)
                            print(row)
                        else:
                            print("Not a match:", row_datetime)
                    except (ValueError, KeyError) as e:
                        # Skip rows with parsing errors or missing 'Timestamp' key
                        print(f"Skipping row due to error: {e}")
                        continue
        except FileNotFoundError:
            print(f"Error: The file {file_path} was not found.")
        print(filtered_data)
        for entry in filtered_data:
            entry['High'] = highTemp
            entry['City'] = self.city
        return filtered_data
    def create_weather_image(self, weather_data):
        """Create a 64x64 weather display image"""
        
        if not weather_data:
            self.pixoo.draw_text_at_location_rgb("No Data", 10, 30, 255, 255, 255)
            return
        
        try:
            temp = str(round(float(weather_data[0]['Fahrenheit'])))
            
            # Draw temperature
            self.pixoo.draw_text_at_location_rgb(f"{temp}°F", 5, 5, 255, 255, 255)
            
            
            # Draw humidity
            humidity = weather_data[0]['Humidity']
            self.pixoo.draw_text_at_location_rgb(f"H:{round(float(humidity))}%", 40,5, 0, 0, 255)
            self.pixoo.draw_text_at_location_rgb(f"C:{round(float(weather_data[0]['Celsius']))}°C", 40, 15, 0, 0, 255)
            # Draw high temperature
            high_temp = weather_data[0]['High']
            self.pixoo.draw_text_at_location_rgb(f"H:{round(float(high_temp))}°F", 5, 15, 255, 0, 0)
        except KeyError as e:
            self.pixoo.draw_text_at_location_rgb(e, 10, 30, 255, 0, 0)
        
        return
    
    def send_to_pixoo(self, image):
        """Send image to Pixoo device via HTTP API"""
        try:

            # Send pixel data to Pixoo
            self.pixoo.push()
        except Exception as e:
            print(f"Error sending to Pixoo: {e}")
    
    def update_display(self):
        """Update the weather display"""
        file_path = 'trashed-1758328976-CurrentTempLog.csv'
        weather_data = self.filter_csv_data(file_path, datetime.now().replace(microsecond=0))
        image = self.create_weather_image(weather_data)
        self.send_to_pixoo(image)
        return image
    
    def run_continuous(self, update_interval=300):
        """Run continuous weather updates every 5 minutes"""
        while True:
            self.update_display()
            time.sleep(update_interval)

# Example usage:
weather_display = PixooWeatherDisplay("192.168.1.100")
weather_display.run_continuous(update_interval=30)