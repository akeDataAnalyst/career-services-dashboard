-- models/staging/stg_course_enrollments.sql
SELECT
    enrollment_id,
    user_id,
    course_id,
    enrollment_date,
    completion_date
FROM
    {{ source('career_services_db', 'course_enrollments') }}