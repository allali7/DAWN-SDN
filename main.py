import time

class Packet:
    def __init__(self, load, timestamp):
        self.load = load
        self.timestamp = timestamp

class Preprocessor:
    def __init__(self, device_capacity, virtual_capacity):
        self.device_capacity = device_capacity
        self.virtual_capacity = virtual_capacity
        self.threads = []

def simulate_attack():
    duration = int(input("Enter the duration of the attack in seconds: "))
    device_capacity = int(input("Enter the capacity for each physical preprocessor: "))
    virtual_capacity = int(input("Enter the capacity for each virtual preprocessor: "))
    processing_time = int(input("Enter the time it takes to process a packet: "))

    preprocessors = [Preprocessor(device_capacity, virtual_capacity)]
    total_physical_preprocessors = 1  # start with 1 because we initialize one preprocessor
    total_virtual_preprocessors = 0
    start_time = time.time()
    for i in range(1, duration + 1):
        intensity = int(input(f"Enter the attack intensity for second {i}: "))

        for preprocessor in preprocessors:
            while intensity > 0 and sum(packet.load for packet in preprocessor.threads) < preprocessor.device_capacity:
                load = min(intensity, virtual_capacity - (preprocessor.threads[-1].load if preprocessor.threads else 0))
                if sum(packet.load for packet in preprocessor.threads) + load > preprocessor.device_capacity:  # don't exceed the device capacity
                    break
                if preprocessor.threads and preprocessor.threads[-1].load < virtual_capacity:
                    preprocessor.threads[-1].load += load
                else:
                    preprocessor.threads.append(Packet(load, time.time()))
                    total_virtual_preprocessors += 1
                intensity -= load
                print(f"Second {i}\nPreprocessor {preprocessors.index(preprocessor) + 1} load: {sum(packet.load for packet in preprocessor.threads)}/{preprocessor.device_capacity}")
                print(f"Virtual Preprocessors: {len(preprocessor.threads)}")

        # At the end of each iteration, check all preprocessors to see if any packets are done processing
        for preprocessor in preprocessors:
            for packet in preprocessor.threads[:]:
                if time.time() - packet.timestamp >= processing_time:
                    preprocessor.threads.remove(packet)
                    print(f"Packet of size {packet.load} has finished processing in Preprocessor {preprocessors.index(preprocessor) + 1}")

        if intensity > 0:  # if there is still intensity left, create a new preprocessor
            new_preprocessor = Preprocessor(device_capacity, virtual_capacity)
            load = min(intensity, virtual_capacity)
            new_preprocessor.threads.append(Packet(load, time.time()))
            total_physical_preprocessors += 1
            total_virtual_preprocessors += 1
            intensity -= load
            preprocessors.append(new_preprocessor)
            print(f"Second {i}\nPreprocessor {len(preprocessors)} load: {sum(packet.load for packet in new_preprocessor.threads)}/{new_preprocessor.device_capacity}")
            print(f"Virtual Preprocessors: {len(new_preprocessor.threads)}")

    print(f"\nTotal Physical Preprocessors: {len(preprocessors)}")
    print(f"Total Virtual Preprocessors: {sum(len(p.threads) for p in preprocessors)}")
    print(f"\nTotal Activated Physical Preprocessors: {total_physical_preprocessors}")
    print(f"Total Activated Virtual Preprocessors: {total_virtual_preprocessors}")


simulate_attack()