CREATE TABLE IF NOT EXISTS orders (
  id serial PRIMARY KEY,
  user_id varchar(250) NOT NULL,
  product_code varchar(250) NOT NULL,
  customer_fullname varchar(250) NOT NULL,
  product_name varchar(250) NOT NULL,
  total_amount FLOAT NOT NULL,
  created_at timestamp NOT NULL
);