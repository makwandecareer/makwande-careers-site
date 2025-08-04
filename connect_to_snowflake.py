import snowflake.connector
import sys
import traceback

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

    # Run a test query
    cur = conn.cursor()
    print("Running test query...", flush=True)
    cur.execute("SELECT CURRENT_TIMESTAMP()")
    result = cur.fetchone()
    print("Current Timestamp:", result[0], flush=True)

    # Cleanup
    cur.close()
    conn.close()
    print("Connection closed", flush=True)

except Exception as e:
    print("An error occurred:", file=sys.stderr, flush=True)
    traceback.print_exc()



