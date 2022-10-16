# Order Management

<p align="center">
  <img src="docs/diagram.png" alt="Flow Chart" />
</p>

## Prerequisites

- [docker](https://www.docker.com/)
- [docker-compose](https://docs.docker.com/compose/)

## How to run

You need to run `docker-compose up` and once the application is ready, you can access the swagger on `http://localhost:8000/docs` . Then you can make the requests to the API and check the results using rabbitMQ and a Postgres client

#### Create Order #1
```json
{
    "user_id": "7c11e1ce2741",
    "product_code": "classic-box"
}
```

#### Create Order #2
```json
{
    "user_id": "7c11e1ce2741",
    "product_code": "family-box"
}
```

#### Create Order #3
```json
{
    "user_id": "7c11e1ce2741",
    "product_code": "veggie-box"
}
```

#### Create Order #4
```json
{
    "user_id": "e6f24d7d1c7e",
    "product_code": "classic-box"
}
```

#### Create Order #5
```json
{
    "user_id": "e6f24d7d1c7e",
    "product_code": "family-box"
}
```

#### Create Order #6
```json
{
    "user_id": "e6f24d7d1c7e",
    "product_code": "veggie-box"
}
```
[Click here for the System Design Document](docs/SystemDesign.md)