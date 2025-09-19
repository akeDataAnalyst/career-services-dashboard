-- models/staging/stg_career_assessments.sql
SELECT
    assessment_id,
    user_id,
    assessment_name,
    completion_date,
    score
FROM
    {{ source('career_services_db', 'career_assessments') }}