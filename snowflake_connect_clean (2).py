import snowflake.connector

try:
    print("Connecting to Snowflake...", flush=True)

    conn = snowflake.connector.connect(
        user='MAKWANDECAREERS',
        password='Makwande@202530',
        account='HPFCRWB-OH67940',
        warehouse='COMPUTE_WH',
        database='AUTOAPPLY_DB',
        schema='AUTOAPPLY_DB',
        role='ACCOUNTADMIN'
    )

    print("Connection established successfully", flush=True)

except Exception as e:
    print(f"Connection failed: {e}", flush=True)
