import asyncio

from highway_sdk.core.metrics import start_prometheus_server
from highway_sdk.core.protocols import DriverTCPClientProtocol
from highway_sdk.core.connectors import TCPReconnectingConnector
from highway_sdk.core.log import LoguruConfig

LoguruConfig.intercept_logging(["*"])
loguru_config = LoguruConfig(name="test", serialize=True)
loguru_config.set_console()
loguru_config.set_file(log_dir="F:\\logs", split_by_name=False)


class MyProtocol(DriverTCPClientProtocol):
    pass


async def main():
    connectors = []
    for port in [8888, 8887, 8889]:
        connector = TCPReconnectingConnector(
            host="127.0.0.1",
            port=port,
            protocol_cls=MyProtocol,
            need_metrics=True,
        )
        connectors.append(connector)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(start_prometheus_server())
        await asyncio.sleep(5)

        for connector in connectors:
            tg.create_task(connector.create())


if __name__ == "__main__":
    asyncio.run(main())
