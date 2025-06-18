import usocket as socket
import network
import ubinascii
import hashlib
import json
from webpage import HTML_PAGE

# Simple WebSocket handshake
def websocket_handshake(reader, writer, headers):
    key = headers["sec-websocket-key"]
    accept = ubinascii.b2a_base64(hashlib.sha1(
        (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()
    ).digest()).strip()

    response = (
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Accept: {accept.decode()}\r\n\r\n"
    )
    writer.write(response.encode())

async def handle_client(reader, writer, motor_controller):
    request_line = await reader.readline()
    headers = {}
    while True:
        line = await reader.readline()
        if line == b"\r\n":
            break
        key, value = line.decode().split(":", 1)
        headers[key.strip().lower()] = value.strip()

    if headers.get("upgrade", "").lower() == "websocket":
        websocket_handshake(reader, writer, headers)
        await handle_websocket(reader, writer, motor_controller)
    else:
        
        writer.write(HTML_PAGE)
        await writer.drain()
        await writer.aclose()



async def handle_websocket(reader, writer, motor_controller):
    forward = 0
    turn = 0

    try:
        while True:
            data = await reader.read(2)
            if not data or len(data) < 2:
                break
            length = data[1] & 127
            if length == 126:
                await reader.read(2)
            elif length == 127:
                await reader.read(8)
            mask = await reader.read(4)
            msg = bytearray()
            for i in range(length):
                byte = await reader.read(1)
                if not byte:
                    raise Exception("Client disconnected")
                msg.append(byte[0] ^ mask[i % 4])

            payload = msg.decode()

            try:
                if payload == "ping":
                    print("receieved ping")
                else:
                    command = json.loads(payload)
                    if "forward" in command:
                        forward = command["forward"]
                    if "turn" in command:
                        turn = command["turn"]
                    motor_controller.control(forward, turn)
            except Exception as e:
                print(payload)
                print("JSON decode error:", e)

    except Exception as e:
        print("WebSocket error:", e)
    finally:
        await writer.aclose()
