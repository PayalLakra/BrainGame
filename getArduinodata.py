import serial  # Import the pySerial module for serial communication
import time    # Import the time module for timing and delays
from pylsl import StreamInfo, StreamOutlet  # Import LSL functionality

# Define the serial port and baud rate (adjust as necessary)
SERIAL_PORT = 'COM4'  # Specify the COM port that the Arduino is connected to
BAUD_RATE = 57600     # Set the baud rate for serial communication

# Initialize the serial connection with the specified port and baud rate
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)

# Variables for packet counting and timing
total_packet_count = 0  # Initialize the packet counter to zero
start_time = time.time()  # Record the start time using the current time

# Define LSL stream information and outlet
info = StreamInfo('ArduinoDataStream', 'EEG', 2, 250, 'float32', 'arduino1234')
outlet = StreamOutlet(info)

def read_arduino_data():
    """Function to read and process data from the Arduino."""
    global total_packet_count  # Use the global packet counter

    # Read 17 bytes of data from the serial port
    raw_data = ser.read(17)
    
    if len(raw_data) == 17:  # Ensure that a full packet (17 bytes) has been received
        # Convert the raw data from bytes to a list of integers
        data_list = list(raw_data)
        
        # Extract and combine the high and low bytes for each channel to form 16-bit integers
        ch1 = data_list[4] << 8 | data_list[5]  # Combine bytes for Channel 1
        ch2 = data_list[6] << 8 | data_list[7]  # Combine bytes for Channel 2
        ch3 = data_list[8] << 8 | data_list[9]  # Combine bytes for Channel 3
        ch4 = data_list[10] << 8 | data_list[11]  # Combine bytes for Channel 4
        ch5 = data_list[12] << 8 | data_list[13]  # Combine bytes for Channel 5
        ch6 = data_list[14] << 8 | data_list[15]  # Combine bytes for Channel 6
        
        # Store the channel data in a list for easy access
        channel_data = [ch1,ch4]

        # Print the channel data values on a single line
        # print(f"Channels: {channel_data[0]}, {channel_data[1]}, {channel_data[2]}, {channel_data[3]}, {channel_data[4]}, {channel_data[5]}")
        
        # Send data to LSL stream
        outlet.push_sample(channel_data)
            
        # Increment the packet count after successfully processing a full packet
        total_packet_count += 1

def print_stats():
    """Function to calculate and print statistics on data reception."""
    global total_packet_count, start_time  # Use the global variables for packet count and start time
    elapsed_time = time.time() - start_time  # Calculate the elapsed time since the start
    # Print the total number of packets received, total time elapsed, and packets per second
    print(f"\nTotal Packets Received: {total_packet_count}")
    print(f"Time Elapsed: {elapsed_time:.2f} seconds")
    print(f"Packets per Second: {total_packet_count / elapsed_time:.2f}")

if __name__ == "__main__":
    # Main loop to continuously read data and update statistics
    try:
        while True:  # Infinite loop to continuously read data from the Arduino
            read_arduino_data()  # Call the function to read and process the data
            # Check if one second has passed since the last reset
            if time.time() - start_time >= 1:
                print_stats()  # Print statistics for the last second
                total_packet_count = 0    # Reset the packet count and start time for the next second
                start_time = time.time()
    except KeyboardInterrupt:
        print("Exiting...")    # When the user interrupts, exit the loop
        print_stats()  # Print final statistics before exiting
    finally:
        ser.close()  # Ensure the serial connection is closed properly
