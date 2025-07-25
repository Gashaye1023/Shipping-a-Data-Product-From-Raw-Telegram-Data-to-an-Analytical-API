{{ config(materialized='view', schema='staging') }}

WITH source AS (
    SELECT 
        id,
        channel_name,
        date,
        (message_data->>'id')::INTEGER AS message_id,
        (message_data->>'date')::TIMESTAMP AS message_timestamp,
        message_data->>'text' AS message_text,
        (message_data->>'sender_id')::INTEGER AS sender_id,
        (message_data->>'has_media')::BOOLEAN AS has_media,
        message_data->>'media_type' AS media_type,
        message_data->>'media_path' AS media_path,
        LENGTH(message_data->>'text') AS message_length
    FROM {{ ref('raw_telegram_messages') }}
)

SELECT
    message_id,
    sender_id,
    date,
    message_text,
    jsonb_extract_path_text(message_data, 'image') AS image_url
FROM source;