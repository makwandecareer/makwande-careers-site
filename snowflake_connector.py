import snowflake.connector

def get_jobs_from_snowflake():
    conn = snowflake.connector.connect(
        user="MAKWANDECAREERS",
        password="Makwande@202530",
        account="hpfcrwb-oh67940",
        warehouse="COMPUTE_WH",
        database="AUTOAPPLY_DB",
        schema="PUBLIC",
        role="ACCOUNTADMIN"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            title, 
            company, 
            country, 
            category, 
            salary, 
            post_advertised_date,
            closing_date 
        FROM MATCHED_JOBS
    """)
    jobs = [
        {
            "title": row[0],
            "company": row[1],
            "country": row[2],
            "category": row[3],
            "salary": row[4],
            "post_advertised_date": row[5],
            "closing_date": row[6]
        }
        for row in cursor.fetchall()
    ]
    cursor.close()
    conn.close()
    return jobs


