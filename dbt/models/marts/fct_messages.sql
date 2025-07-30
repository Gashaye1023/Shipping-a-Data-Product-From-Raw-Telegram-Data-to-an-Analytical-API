{{ config(materialized='table', schema='data_marts') }}

SELECT
    message_id,
    date,
    LENGTH(text) AS message_length,
    channel_id
FROM {{ ref('stg_telegram_messages') }};