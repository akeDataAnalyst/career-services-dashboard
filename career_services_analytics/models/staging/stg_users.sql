-- models/staging/stg_users.sql

SELECT
    user_id,
    registration_date,
    country,
    career_goals
FROM
    -- This macro references the raw 'users' table you defined in sources.yml
	{{ source('career_services_db', 'users') }}