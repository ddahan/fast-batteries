# Messaging

In any app, after performing an HTTP action, a message (success or error) should be displayed. Architecturally, these messages can either come entirely from the back-end, or the back-end can return only the necessary data while the front-end generates and displays the message.

From a separation of concerns perspective, the front-end is typically responsible for constructing and displaying messages. However, it's often easier to handle message generation on the back-end, especially for errors that aren't predefined (e.g., when a form field violates a constraint).

Currently in Fast Batteries:

- Success messages are generated on the front-end.
- For convenience, error messages are generated on the back-end and displayed automatically.
  
In the future, for better consistency, we could explore handling all message types on the front-end, even though this approach increases the coupling between the front-end and back-end.

# Custom Error management

### How does it work?

  There are 3 kinds of failed requests which could raise an Exception:
  - Pydantic `RequestValidationError` are raised automatically (with a `422` status) when provided data is invalid
  - `ProjectAPIException` inherited classes are custom exceptions defined by the developper with a specific message. They should be run in routes (not in business logic).
    - They can be overrided overrided when raised (for example to change the default message)
    - They support string formatting to inject dynamic data into the messages (at raising time)
  - All other uncaught errors are handle gracefully (with a `500` status but a clean message)

All errors return a `ErrorPayload` class:
  - Errors are split in 3 different categories  (`general`, `field`, `nonfield`) to help front-end know how to display them:
    - `general` → to display in a notification toast
    - `nonfield` → to display at the top level of a form
    - `field` → to display near a wrong field
  - Multiple errors can be returned in a single `ErrorPayload` response
