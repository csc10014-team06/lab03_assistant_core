-- Lab 5, Part F: Real questions about the assistant on assistant.db (SELECT-only)

-- F1 (How many questions per intent?)
SELECT intent, COUNT(*) AS requests
FROM interaction
GROUP BY intent
ORDER BY requests DESC, intent;

-- F2 (Average time taken per intent?)
SELECT intent, ROUND(AVG(latency_ms), 1) AS avg_latency_ms
FROM interaction
GROUP BY intent
ORDER BY avg_latency_ms DESC, intent;

-- F3 (Which topics got the most thumbs-down?)
SELECT i.topic, COUNT(*) AS thumbs_down
FROM interaction i
JOIN feedback f ON f.request_id = i.request_id
WHERE f.rating = -1
  AND i.topic IS NOT NULL
GROUP BY i.topic
ORDER BY thumbs_down DESC, i.topic;
