-- models/staging/stg_resume_uploads.sql
SELECT
    upload_id,
    user_id,
    upload_date
FROM
    {{ source('career_services_db', 'resume_uploads') }}