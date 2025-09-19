-- models/marts/fact_user_activity.sql

SELECT
    u.user_id,
    u.registration_date,
    COUNT(DISTINCT ja.application_id) AS total_applications,
    COUNT(DISTINCT pv.view_id) AS total_profile_views,
    COUNT(DISTINCT ce.enrollment_id) AS total_courses_enrolled,
    COUNT(DISTINCT ru.upload_id) AS total_resumes_uploaded,
    COUNT(DISTINCT ca.assessment_id) AS total_assessments_taken
FROM
    {{ ref('stg_users') }} u
LEFT JOIN
    {{ ref('stg_job_applications') }} ja ON u.user_id = ja.user_id
LEFT JOIN
    {{ ref('stg_profile_views') }} pv ON u.user_id = pv.viewed_user_id
LEFT JOIN
    {{ ref('stg_course_enrollments') }} ce ON u.user_id = ce.user_id
LEFT JOIN
    {{ ref('stg_resume_uploads') }} ru ON u.user_id = ru.user_id
LEFT JOIN
    {{ ref('stg_career_assessments') }} ca ON u.user_id = ca.user_id
GROUP BY
    u.user_id,
    u.registration_date