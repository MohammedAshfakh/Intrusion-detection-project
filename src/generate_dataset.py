import random
import csv

protocols = ["tcp","udp","icmp"]
services = ["http","ftp","dns","smtp","ecr_i"]
labels = ["normal","attack"]

with open("dataset/dataset.csv","w",newline="") as f:
    writer = csv.writer(f)

    writer.writerow(["duration","protocol_type","service","src_bytes","dst_bytes","flag","count","attack"])

    for i in range(1000):

        row = [
            random.randint(0,10),
            random.choice(protocols),
            random.choice(services),
            random.randint(0,1500),
            random.randint(0,1500),
            "SF",
            random.randint(1,10),
            random.choice(labels)
        ]

        writer.writerow(row)

print("Dataset generated successfully")
