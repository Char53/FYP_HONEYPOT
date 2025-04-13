
from faker import Faker

fake = Faker()
for i in range(5):
    with open(f"cloud_file_{i+1}.txt", "w") as f:
        f.write(fake.text(max_nb_chars=500))
