# How the WebSocket Messaging System Works

This FastAPI module implements a robust, real-time messaging backend using WebSockets and Redis Pub/Sub. It allows clients to connect to dynamic channels ("rooms"), exchange messages, and broadcast them to all connected clients in the same room — even across multiple backend instances.

## 🔁 Workflow

### 1. Client Connects

- Client connects to /ws/room/{room} via WebSocket.
- The server checks if the room (e.g. chat) is supported.
- If allowed, the client is added to the appropriate in-memory room on this server

### 2. Client Sends Message

- The client sends a JSON payload like:
```json
{
  "room": "chat",
  "name": "Alice",
  "message": "Hello!"
}
```
- The server validates the payload using `WSChatMessage` Pydantic schema.
- The message is published to Redis on the channel `room:chat`.

### 3. Redis Fan-out

- All backend instances are subscribed to `room:*` Redis channels.
- When Redis receives a message on `room:chat`, it forwards it to each subscribed server.
- Each server then re-broadcasts the message to its local clients in the matching chat room.


## 🔒 Safety & Features
- Unknown rooms are rejected (1008 Policy Violation)
- Heartbeat support (keeps connection alive)
- Dead clients are automatically removed
- Redis reconnects on error
- Future room types can be added in `SUPPORTED_SLUGS`
