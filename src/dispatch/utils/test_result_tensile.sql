 
--# 分区  DROP TABLE dispatch_organization_test.test_result_tensile;

CREATE TABLE dispatch_organization_test.test_result_tensile (
	id serial4 NOT NULL,
	test_sample_id int4 NOT NULL,
	sample_shape varchar(1) NULL,
	tested_thickness numeric(20, 10) NULL,
	tested_width numeric(20, 10) NULL,
	tested_diameter numeric(20, 10) NULL,
	value_mpa numeric(20, 10) NULL,
	yield_tt0_5 numeric(20, 10) NULL,
	yield_high numeric(20, 10) NULL,
	yield_rp0_2 numeric(20, 10) NULL,
	yield_low numeric(20, 10) NULL,
	elongation_code varchar(1) NULL,
	elongation_a565 numeric(20, 10) NULL,
	elongation_a200 numeric(20, 10) NULL,
	elongation_a50 numeric(20, 10) NULL,
	elongation_8 numeric(20, 10) NULL,
	elongation_2 numeric(20, 10) NULL,
	elongation_a80 numeric(20, 10) NULL,
	flex_form_data json NULL,
	is_deleted int4 NULL,
	created_by varchar NULL,
	created_at timestamp NULL,
	updated_at timestamp NULL,
	updated_by varchar NULL,
	CONSTRAINT test_result_tensile_pkey PRIMARY KEY (id,created_at)
) PARTITION BY RANGE (created_at);

CREATE TABLE dispatch_organization_test.test_result_tensile_y2023m01 PARTITION OF dispatch_organization_test.test_result_tensile
FOR VALUES FROM ('2023-01-01 00:00:00') TO ('2023-02-01 00:00:00');


CREATE TABLE dispatch_organization_test.test_result_tensile_y2023m02 PARTITION OF dispatch_organization_test.test_result_tensile
FOR VALUES FROM ('2023-02-01 00:00:00') TO ('2023-03-01 00:00:00');