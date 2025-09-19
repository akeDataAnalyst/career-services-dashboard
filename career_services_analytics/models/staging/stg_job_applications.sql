-- models/staging/stg_job_applications.sql
SELECT
    application_id,
    user_id,
    job_id,
    application_date,
    application_status
FROM
    {{ source('career_services_db', 'job_applications') }}