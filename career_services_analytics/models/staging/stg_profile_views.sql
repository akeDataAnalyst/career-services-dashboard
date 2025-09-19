-- models/staging/stg_profile_views.sql
SELECT
    view_id,
    viewer_id,
    viewed_user_id,
    view_date
FROM
    {{ source('career_services_db', 'profile_views') }}