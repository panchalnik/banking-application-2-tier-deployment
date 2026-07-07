import boto3
import os
import sys
import pymysql

# Create SSM client
client = boto3.client("ssm", region_name="us-east-1")

# Read parameters from Parameter Store
params = {
    os.path.basename(p["Name"]): p["Value"]
    for p in client.get_parameters_by_path(
        Path="/application/banking",
        WithDecryption=True
    )["Parameters"]
}

# Required parameters
required = ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD", "DB_PORT"]

missing = [k for k in required if k not in params]

# Print parameter status
for k in required:
    print(f"{k}: {'✅' if k in params else '❌'}")

# Exit if any parameter is missing
if missing:
    print(f"Missing Parameters: {missing}")
    sys.exit(1)

# Database connectivity test
try:
    connection = pymysql.connect(
        host=params["DB_HOST"],
        user=params["DB_USER"],
        password=params["DB_PASSWORD"],
        database=params["DB_NAME"],
        port=int(params["DB_PORT"]),
        connect_timeout=10
    )

    cursor = connection.cursor()

    cursor.execute("SHOW TABLES;")

    tables = [row[0] for row in cursor.fetchall()]

    connection.close()

    print(f"\nDatabase : {params['DB_NAME']}")
    print(f"Tables   : {tables}")

except Exception as e:
    print("DB ERROR:", e)
    sys.exit(1)

print("\nSmoke Test Passed ✅")