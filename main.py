
import time
import random
import matplotlib.pyplot as plt


class Packet:
    def __init__(self, load, timestamp, packet_type, ttl=-1):
        self.load = load
        self.timestamp = timestamp * 1e6  # Convert to microseconds
        self.packet_type = packet_type
        self.ttl = ttl


class Preprocessor:
    def __init__(self, device_capacity, virtual_capacity):
        self.device_capacity = device_capacity
        self.virtual_capacity = virtual_capacity
        self.threads = []
        self.current_load = 0
        self.total_unchecked_packets = 0
        self.total_whitelisted_packets = 0
        self.total_blacklisted_packets = 0
        self.total_signature_packets = 0
        self.times_reused = 0
        self.total_expired_packets = 0

    def add_packet(self, packet):
        if not self.threads or self.threads[-1].load >= self.virtual_capacity:
            self.threads.append(packet)
        else:
            self.threads[-1].load += packet.load
        self.current_load += packet.load

        if packet.packet_type == "unchecked":
            self.total_unchecked_packets += 1
            self.times_reused += 1
        elif packet.packet_type == "whitelisted":
            self.total_whitelisted_packets += 1
        elif packet.packet_type == "blacklisted":
            self.total_blacklisted_packets += 1
        elif packet.packet_type == "signature-based":
            self.total_signature_packets += 1

    def remove_packet(self, packet):
        self.threads.remove(packet)
        self.current_load -= packet.load


def generate_packet(load, packet_types, ttl_values):
    packet_type = random.choice(packet_types)
    ttl = ttl_values[packet_type]
    return Packet(load, time.time(), packet_type, ttl)

def check_and_remove_expired_packets(preprocessor, processing_times, preprocessors):
    current_time_microseconds = time.time() * 1e6  # Convert current time to microseconds
    for packet in preprocessor.threads[:]:
        if packet.ttl != -1 and current_time_microseconds - packet.timestamp >= packet.ttl:
            preprocessor.total_expired_packets += 1
            preprocessor.remove_packet(packet)
            print(f"Packet of size {packet.load} and type {packet.packet_type} has expired TTL in Preprocessor {preprocessors.index(preprocessor) + 1}")
            # remove these lines if ttl and adding to unchecked is causing delay, might be better to drop
            # Create a new packet with the same load but marked as "unchecked"
            # unchecked_packet = Packet(packet.load, time.time(), "unchecked")
            # preprocessor.add_packet(unchecked_packet)

            # # Remove the expired packet
            # preprocessor.remove_packet(packet)
        elif current_time_microseconds - packet.timestamp >= processing_times[packet.packet_type]:
            preprocessor.remove_packet(packet)
            print(f"Packet of size {packet.load} and type {packet.packet_type} has finished processing in Preprocessor {preprocessors.index(preprocessor) + 1}")

def allocate_packet_to_preprocessor(packet, preprocessors, device_capacity, virtual_capacity, processing_times):
    for preprocessor in preprocessors:
        check_and_remove_expired_packets(preprocessor, processing_times, preprocessors)

        # Check for an available virtual preprocessor
        if preprocessor.threads and preprocessor.threads[-1].load + packet.load <= virtual_capacity:
            preprocessor.add_packet(packet)
            return
        # Check for an underutilized physical preprocessor
        elif preprocessor.current_load + packet.load <= device_capacity:
            preprocessor.add_packet(packet)
            return

    # If no available space in current preprocessors, start a new one
    new_preprocessor = Preprocessor(device_capacity, virtual_capacity)
    new_preprocessor.add_packet(packet)
    preprocessors.append(new_preprocessor)
    print(f"New Preprocessor {len(preprocessors)} initialized with load: {packet.load}/{new_preprocessor.device_capacity}")

def plot_packet_distribution(preprocessors):
    labels = [f"P{idx+1}" for idx in range(len(preprocessors))]
    unchecked = [p.total_unchecked_packets for p in preprocessors]
    whitelisted = [p.total_whitelisted_packets for p in preprocessors]
    blacklisted = [p.total_blacklisted_packets for p in preprocessors]
    signature_based = [p.total_signature_packets for p in preprocessors]

    x = range(len(labels))
    width = 0.2

    fig, ax = plt.subplots()
    ax.bar(x, unchecked, width, label='Unchecked')
    ax.bar([i + width for i in x], whitelisted, width, label='Whitelisted')
    ax.bar([i + width*2 for i in x], blacklisted, width, label='Blacklisted')
    ax.bar([i + width*3 for i in x], signature_based, width, label='Signature-based')

    ax.set_xlabel('Preprocessor ID')
    ax.set_ylabel('Number of Packets')
    ax.set_title('Packet Distribution per Preprocessor')
    ax.set_xticks([i + width*1.5 for i in x])
    ax.set_xticklabels(labels)
    ax.legend()

    plt.show()

def plot_virtual_preprocessors(preprocessors):
    labels = [f"P{idx+1}" for idx in range(len(preprocessors))]
    virtuals = [len(p.threads) for p in preprocessors]

    plt.bar(labels, virtuals, color='blue')
    plt.xlabel('Preprocessor ID')
    plt.ylabel('Number of Virtual Preprocessors')
    plt.title('Virtual Preprocessors per Physical Preprocessor')
    plt.show()

def plot_utilization(preprocessors):
    labels = [f"P{idx+1}" for idx in range(len(preprocessors))]
    utilization = [(p.current_load / p.device_capacity) * 100 for p in preprocessors]

    plt.bar(labels, utilization, color='green')
    plt.xlabel('Preprocessor ID')
    plt.ylabel('Utilization (%)')
    plt.title('Utilization of Physical Preprocessors')
    plt.ylim(0, 100)
    plt.show()

def plot_times_reused(preprocessors):
    labels = [f"P{idx+1}" for idx in range(len(preprocessors))]
    times_reused = [p.times_reused for p in preprocessors]

    plt.bar(labels, times_reused, color='red')
    plt.xlabel('Preprocessor ID')
    plt.ylabel('Times Reused')
    plt.title('Times Reused for Each Preprocessor')
    plt.show()

def plot_ttl_expiry(preprocessors):
    labels = [f"P{idx+1}" for idx in range(len(preprocessors))]
    expired = [p.total_expired_packets for p in preprocessors]

    plt.bar(labels, expired, color='purple')
    plt.xlabel('Preprocessor ID')
    plt.ylabel('Number of Packets Expired')
    plt.title('Packet TTL Expiry per Preprocessor')
    plt.show()

def display_summary_table(preprocessors):
    # Create a new figure
    fig, ax = plt.subplots(figsize=(12, len(preprocessors) * 0.5))  # Adjust the size based on the number of preprocessors
    ax.axis('off')  # Turn off the axis

    # Data for the table
    columns = ["Physical Preprocessor", "Times Reused", "Unchecked", "Whitelisted", "Blacklisted", "Signature"]
    cell_data = []
    for idx, preprocessor in enumerate(preprocessors, 1):
        row = [
            "P" + str(idx),
            preprocessor.times_reused,
            preprocessor.total_unchecked_packets,
            preprocessor.total_whitelisted_packets,
            preprocessor.total_blacklisted_packets,
            preprocessor.total_signature_packets
        ]
        cell_data.append(row)

    # Create the table
    table = ax.table(cellText=cell_data, colLabels=columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(columns))))

    # Adjust the table properties for better aesthetics
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    plt.title("Summary Table")
    plt.show()

def plot_processing_time(avg_processing_times):
    labels = list(avg_processing_times.keys())
    times = [time_val / 1000 for time_val in avg_processing_times.values()]  # Convert to milliseconds

    plt.bar(labels, times, color='orange')
    plt.xlabel('Packet Type')
    plt.ylabel('Average Processing Time (ms)')  # Adjust the label to ms
    plt.title('Average Processing Time per Packet Type')
    plt.show()


def generate_intensities():
    intensities = []

    # Seconds 1-30: Linearly increase from 5000 to 15000
    for i in range(30):
        intensity = 5000 + (i / 29) * (15000 - 5000)
        intensities.append(int(intensity))

    # Seconds 31-90: Stay at peak intensity, around 20000
    intensities.extend([20000] * 60)

    # Seconds 91-120: Linearly decrease from 15000 to 5000
    for i in range(30):
        intensity = 15000 - (i / 29) * (15000 - 5000)
        intensities.append(int(intensity))

    return intensities

def input_intensities_manually(duration):
    intensities = []
    for i in range(1, duration + 1):
        intensity = int(input(f"Enter the attack intensity for second {i}: "))
        intensities.append(intensity)
    return intensities

def simulate_attack():
    # Input gathering section
    # intensities = []
    # duration = int(input("Enter the duration of the attack in seconds: "))
    # Input gathering section
    choice = input("Do you want to use the default intensity pattern? (yes/no): ").strip().lower()

    if choice == 'yes':
        intensities = generate_intensities()
        duration = len(intensities)
    else:
        duration = int(input("Enter the duration of the attack in seconds: "))
        intensities = input_intensities_manually(duration)

    device_capacity = int(input("Enter the capacity for each physical preprocessor: "))
    virtual_capacity = int(input("Enter the capacity for each virtual preprocessor: "))
    processing_times = {
        "unchecked": int(input("Enter the time it takes to process an unchecked packet (in microseconds): ")),
        "whitelisted": int(input("Enter the time it takes to process a whitelisted packet (in microseconds): ")),
        "blacklisted": int(input("Enter the time it takes to process a blacklisted packet (in microseconds): ")),
        "signature-based": int(input("Enter the time it takes to process a signature-based packet (in microseconds): "))
    }

    ttl_values = {
        "unchecked": -1,
        "whitelisted": int(
            input("Enter the TTL for a whitelisted packet in microseconds (enter -1 if there is no TTL): ")),
        "blacklisted": int(
            input("Enter the TTL for a blacklisted packet in microseconds (enter -1 if there is no TTL): ")),
        "signature-based": -1
    }

    remaining_percentage = 100
    packet_distribution = {}
    packet_distribution["unchecked"] = int(
        input(f"Enter the percentage of unchecked packets (from 0 to {remaining_percentage}): "))
    remaining_percentage -= packet_distribution["unchecked"]

    if remaining_percentage > 0:
        packet_distribution["whitelisted"] = int(
            input(f"Enter the percentage of whitelisted packets (from 0 to {remaining_percentage}): "))
        remaining_percentage -= packet_distribution["whitelisted"]

    if remaining_percentage > 0:
        packet_distribution["blacklisted"] = int(
            input(f"Enter the percentage of blacklisted packets (from 0 to {remaining_percentage}): "))
        remaining_percentage -= packet_distribution["blacklisted"]

    packet_distribution["signature-based"] = remaining_percentage
    packet_types = []
    for packet_type, percentage in packet_distribution.items():
        packet_types.extend([packet_type] * percentage)

    preprocessors = [Preprocessor(device_capacity, virtual_capacity)]

    time_points = []
    active_preprocessors_data = []  # For physical preprocessors
    virtual_preprocessors_data = []  # For virtual preprocessors

    # Collecting utilization data for each preprocessor
    utilization_data = []

    # for i in range(1, duration + 1):
    #     intensity = int(input(f"Enter the attack intensity for second {i}: "))
    #     intensities.append(intensity)

    for i in range(1, duration + 1):
        intensity = intensities[i - 1]

        for preprocessor in preprocessors:
            while intensity > 0:
                load = min(intensity, virtual_capacity)
                packet = generate_packet(load, packet_types, ttl_values)
                allocate_packet_to_preprocessor(packet, preprocessors, device_capacity, virtual_capacity,processing_times)
                intensity -= load
                print(
                    f"Second {i}\nVirtual Preprocessors in Preprocessor {len(preprocessors)}: {len(preprocessors[-1].threads)}")
        # Append data for plotting
        time_points.append(i)
        active_preprocessors_data.append(len(preprocessors))
        virtual_preprocessors_data.append(sum(len(p.threads) for p in preprocessors))
        current_utilization = [p.current_load / p.device_capacity * 100 for p in preprocessors]
        utilization_data.append(sum(current_utilization) / len(current_utilization))  # Average utilization

        # If there's remaining intensity, initialize a new preprocessor
        if intensity > 0:
            new_preprocessor = Preprocessor(device_capacity, virtual_capacity)
            load = min(intensity, virtual_capacity)
            packet = generate_packet(load, packet_types, ttl_values)
            new_preprocessor.add_packet(packet)
            preprocessors.append(new_preprocessor)
            print(
                f"Second {i}\nNew Preprocessor {len(preprocessors)} initialized with load: {load}/{new_preprocessor.device_capacity}")
            print(f"Virtual Preprocessors: {len(new_preprocessor.threads)}")

    print(f"\nTotal Physical Preprocessors: {len(preprocessors)}")
    print(f"Total Virtual Preprocessors: {sum(len(p.threads) for p in preprocessors)}")


    # Display the summary table
    print("\n---------------------------------------------------------------------------------------------")
    print("| Physical Preprocessor | Times Reused | Unchecked | Whitelisted | Blacklisted | Signature |")
    print("----------------------------------------------------------------------------------------------")
    for idx, preprocessor in enumerate(preprocessors, 1):
        print("|", "P" + str(idx), " " * (20 - len(str(idx))), "|",
              preprocessor.times_reused, " " * (11 - len(str(preprocessor.times_reused))), "|",
              preprocessor.total_unchecked_packets, " " * (8 - len(str(preprocessor.total_unchecked_packets))), "|",
              preprocessor.total_whitelisted_packets, " " * (10 - len(str(preprocessor.total_whitelisted_packets))),
              "|",
              preprocessor.total_blacklisted_packets, " " * (10 - len(str(preprocessor.total_blacklisted_packets))),
              "|",
              preprocessor.total_signature_packets, " " * (8 - len(str(preprocessor.total_signature_packets))), "|")
        print("----------------------------------------------------------------------------------------------")

        # Plotting the data
    # plt.plot(time_points, active_preprocessors_data, '-o', color='blue')
    # plt.xlabel('Time (seconds)')
    # plt.ylabel('Number of Active Preprocessors')
    # plt.title('Active Preprocessors Over Time')
    # plt.grid(True)
    # plt.show()


    # Plotting the number of active preprocessors over time
    plt.figure(figsize=(10, 5))
    plt.plot(time_points, active_preprocessors_data, '-o', color='blue')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Number of Active Preprocessors')
    plt.title('Active Preprocessors Over Time')
    plt.grid(True)
    plt.show()

    # Plotting the number of active virtual preprocessors over time
    plt.figure(figsize=(10, 5))
    plt.plot(time_points, virtual_preprocessors_data, '-o', color='green', label='Virtual Preprocessors')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Number of Active Virtual Preprocessors')
    plt.title('Active Virtual Preprocessors Over Time')
    plt.grid(True)
    plt.legend()
    plt.show()


    # Plotting the average utilization over time
    plt.figure(figsize=(10, 5))
    plt.plot(time_points, utilization_data, '-o', color='green')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Average Utilization (%)')
    plt.title('Average Utilization Over Time')
    plt.grid(True)
    plt.ylim(0, 300)  # Setting y-axis limits to for percentage
    plt.show()

    # Plotting the graphs
    plot_packet_distribution(preprocessors)
    plot_virtual_preprocessors(preprocessors)
    plot_utilization(preprocessors)
    plot_times_reused(preprocessors)
    plot_ttl_expiry(preprocessors)
    display_summary_table(preprocessors)


simulate_attack()


