from unittest import TestCase
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from importlib import reload


class mainTest(TestCase):
    def creat_mock_call(self, status, json={}):
        response = MagicMock()
        response.status = status
        response.json = AsyncMock(return_value=json)
        return response

    def reload_main(self):
        # we can't import the module like usual, because it would break the test while trying
        # to set up all his dependencies that were not mocked yet. But once the module is loaded,
        # it can not update the modules that were previously patched. So we need to reload
        # the main module every time
        from app import main

        reload(main)
        from app.main import app

        return app

    @patch("app.database.engine")
    @patch("app.database.SessionLocal")
    @patch("app.pika_client.PikaClient")
    @patch("aiohttp.ClientSession.get")
    def test_product_not_found(
        self, mock_get, mock_pika, mock_database_session, mock_database_engine
    ):

        mock_first_call = self.creat_mock_call(404)
        mock_second_call = self.creat_mock_call(200)

        mock_get.side_effect = AsyncMock(
            side_effect=[mock_first_call, mock_second_call]
        )
        mock_pika.return_value = MagicMock()
        mock_database_session.return_value = MagicMock()

        app = self.reload_main()

        client = TestClient(app)

        response = client.post(
            "/orders", json={"user_id": "7c11e1ce2741", "product_code": "classic-box"}
        )

        assert response.status_code == 400
        assert response.text == '{"detail":"Product not found"}'

    @patch("app.database.engine")
    @patch("app.database.SessionLocal")
    @patch("app.pika_client.PikaClient")
    @patch("aiohttp.ClientSession.get")
    def test_user_not_found(
        self, mock_get, mock_pika, mock_database_session, mock_database_engine
    ):

        mock_first_call = self.creat_mock_call(200)
        mock_second_call = self.creat_mock_call(404)

        mock_get.side_effect = AsyncMock(
            side_effect=[mock_first_call, mock_second_call]
        )
        mock_pika.return_value = MagicMock()
        mock_database_session.return_value = MagicMock()

        app = self.reload_main()

        client = TestClient(app)

        response = client.post(
            "/orders", json={"user_id": "7c11e1ce2741", "product_code": "classic-box"}
        )

        assert response.status_code == 400
        assert response.text == '{"detail":"User not found"}'

    @patch("app.database.engine")
    @patch("app.database.SessionLocal")
    @patch("app.pika_client.PikaClient")
    @patch("aiohttp.ClientSession.get")
    def test_error_on_product_api(
        self, mock_get, mock_pika, mock_database_session, mock_database_engine
    ):
        mock_first_call = self.creat_mock_call(500)
        mock_second_call = self.creat_mock_call(200)

        mock_get.side_effect = AsyncMock(
            side_effect=[mock_first_call, mock_second_call]
        )
        mock_pika.return_value = MagicMock()
        mock_database_session.return_value = MagicMock()

        app = self.reload_main()

        client = TestClient(app)

        response = client.post(
            "/orders", json={"user_id": "7c11e1ce2741", "product_code": "classic-box"}
        )

        assert response.status_code == 500
        assert response.text == '{"detail":"Unexpected error"}'

    @patch("app.database.engine")
    @patch("app.database.SessionLocal")
    @patch("app.pika_client.PikaClient")
    @patch("aiohttp.ClientSession.get")
    def test_error_on_user_api(
        self, mock_get, mock_pika, mock_database_session, mock_database_engine
    ):
        mock_first_call = self.creat_mock_call(200)
        mock_second_call = self.creat_mock_call(500)

        mock_get.side_effect = AsyncMock(
            side_effect=[mock_first_call, mock_second_call]
        )
        mock_pika.return_value = MagicMock()
        mock_database_session.return_value = MagicMock()

        app = self.reload_main()

        client = TestClient(app)

        response = client.post(
            "/orders", json={"user_id": "7c11e1ce2741", "product_code": "classic-box"}
        )

        assert response.status_code == 500
        assert response.text == '{"detail":"Unexpected error"}'

    @patch("app.database.engine")
    @patch("app.database.SessionLocal")
    @patch("app.pika_client.PikaClient")
    @patch("aiohttp.ClientSession.get")
    def test_error_saving(
        self, mock_get, mock_pika, mock_database_session, mock_database_engine
    ):
        mock_first_call = self.creat_mock_call(
            200, {"name": "Classic Box", "price": 9.99}
        )
        mock_second_call = self.creat_mock_call(
            200, {"firstName": "Ada", "lastName": "Lovelace"}
        )

        mock_db = MagicMock()
        mock_db.refresh.side_effect = Exception("boom db")
        mock_database_session.return_value = mock_db

        mock_get.side_effect = AsyncMock(
            side_effect=[mock_first_call, mock_second_call]
        )
        mock_pika.return_value = MagicMock()

        app = self.reload_main()

        client = TestClient(app)

        response = client.post(
            "/orders", json={"user_id": "7c11e1ce2741", "product_code": "classic-box"}
        )
        assert response.status_code == 503
        assert response.text == '{"detail":"server is unavaible"}'
        mock_db.commit.assert_not_called()
        mock_db.flush.assert_called_once()
        mock_db.rollback.assert_called_once()

    @patch("app.database.engine")
    @patch("app.database.SessionLocal")
    @patch("app.pika_client.PikaClient")
    @patch("aiohttp.ClientSession.get")
    def test_error_publishing(
        self, mock_get, mock_pika, mock_database_session, mock_database_engine
    ):
        mock_first_call = self.creat_mock_call(
            200, {"name": "Classic Box", "price": 9.99}
        )
        mock_second_call = self.creat_mock_call(
            200, {"firstName": "Ada", "lastName": "Lovelace"}
        )

        mock_get.side_effect = AsyncMock(
            side_effect=[mock_first_call, mock_second_call]
        )

        def updateOrder(order):
            order.created_at = MagicMock()

        mock_db = MagicMock()
        mock_db.refresh = updateOrder
        mock_database_session.return_value = mock_db

        mock_pika_client = MagicMock()
        mock_pika_client.send_message.side_effect = Exception("boom rabbitmq")
        mock_pika.return_value = mock_pika_client

        app = self.reload_main()

        client = TestClient(app)

        response = client.post(
            "/orders", json={"user_id": "7c11e1ce2741", "product_code": "classic-box"}
        )
        assert response.status_code == 503
        assert response.text == '{"detail":"server is unavaible"}'
        mock_db.commit.assert_not_called()
        mock_db.rollback.assert_called_once()

    @patch("app.database.engine")
    @patch("app.database.SessionLocal")
    @patch("app.pika_client.PikaClient")
    @patch("aiohttp.ClientSession.get")
    def test_message_published(
        self, mock_get, mock_pika, mock_database_session, mock_database_engine
    ):
        mock_first_call = self.creat_mock_call(
            200, {"name": "Classic Box", "price": 9.99}
        )
        mock_second_call = self.creat_mock_call(
            200, {"firstName": "Ada", "lastName": "Lovelace"}
        )

        mock_get.side_effect = AsyncMock(
            side_effect=[mock_first_call, mock_second_call]
        )

        def updateOrder(order):
            order.created_at = MagicMock()

        mock_db = MagicMock()
        mock_db.refresh = updateOrder
        mock_database_session.return_value = mock_db

        mock_pika_client = MagicMock()
        mock_pika.return_value = mock_pika_client

        app = self.reload_main()

        client = TestClient(app)

        response = client.post(
            "/orders", json={"user_id": "7c11e1ce2741", "product_code": "classic-box"}
        )

        assert response.status_code == 200
        assert response.text == '{"detail":"order created successfully"}'
        mock_db.commit.assert_called_once()
        mock_db.rollback.assert_not_called()

        pika_args = mock_pika_client.send_message.call_args[0][0]
        assert pika_args["producer"] == "order-management"
        assert pika_args["payload"]["order"]["customer_fullname"] == "Ada Lovelace"
        assert pika_args["payload"]["order"]["product_name"] == "Classic Box"
        assert pika_args["payload"]["order"]["total_amount"] == 9.99

        db_args = mock_db.add.call_args[0][0]
        assert db_args.user_id == "7c11e1ce2741"
        assert db_args.product_code == "classic-box"
        assert db_args.customer_fullname == "Ada Lovelace"
        assert db_args.product_name == "Classic Box"
        assert db_args.total_amount == 9.99
