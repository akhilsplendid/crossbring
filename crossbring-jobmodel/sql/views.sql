-- Convenience views
CREATE OR REPLACE VIEW jobmodel.v_current_postings AS
SELECT fp.*
FROM jobmodel.fact_posting fp
WHERE fp.is_current;

CREATE OR REPLACE VIEW jobmodel.v_postings_by_region AS
SELECT dl.region, dl.city, count(*) AS postings
FROM jobmodel.v_current_postings fp
LEFT JOIN jobmodel.dim_location dl ON dl.location_id = fp.location_id
GROUP BY dl.region, dl.city
ORDER BY postings DESC;

