# import pytest
# import socketserver
# import threading

# HOST, PORT = "127.0.0.1", 8888


# @pytest.fixture(scope="session")
# def mock_tcp_server(request):
#     handler_class = request.param
#     with socketserver.ThreadingTCPServer((HOST, PORT), handler_class) as server:
#         server_thread = threading.Thread(target=server.serve_forever)
#         server_thread.daemon = True
#         server_thread.start()
#         yield server
