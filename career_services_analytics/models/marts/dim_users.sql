-- models/marts/dim_users.sql
SELECT
    user_id,
    registration_date,
    country,
    career_goals
FROM
    {{ ref('stg_users') }}