## Authentication

### Potential choices

While session authentication is absolutely a valid method (and somehow simpler), as we're using Social Auth that uses JWT, and JWT is well-known standard, I decided to go with it. Let's compare the implications below:

| **Aspect**                 | **Session Authentication**                                                                                   | **JWT Authentication**                                                                                     |
|----------------------------|------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| **Storage**                | Sessions are stored on the server, with a session ID sent to the client, usually as a cookie.               | Tokens are stateless and stored on the client, often in `localStorage`, `sessionStorage`, or cookies.     |
| **Scalability**            | Storing sessions on the server can make horizontal scaling challenging, requiring shared storage solutions like Redis. | Stateless tokens make scaling easy, ideal for distributed and serverless architectures.                  |
| **Revocation**             | Sessions can be easily revoked by removing the session ID from the database.                              | Revoking JWTs is complex and requires implementing a blacklist or a short-lived token system.            |
| **Security**               | The server controls the session, reducing token exposure to the client.                                   | Stateless design means tokens are exposed on the client, increasing the risk if the token is compromised.|
| **Implementation**         | Simplified by many web frameworks with built-in support for session handling.                             | Requires manual implementation or libraries, but offers more flexibility for modern architectures.       |
| **CSRF Protection**        | Sessions are vulnerable to Cross-Site Request Forgery attacks unless CSRF tokens are implemented.          | Tokens sent in headers are inherently resistant to CSRF attacks.                                         |
| **Size Overhead**          | Sessions use lightweight IDs, minimizing bandwidth usage.                                                  | JWTs include claims and a signature, resulting in larger payloads.                                       |
| **Expiration Management**  | Handled on the server, with easy control over session duration.                                            | Requires refresh tokens or periodic re-authentication for better security.                               |
| **Best Use Case**          | Suitable for small to medium-sized applications where scalability isn’t a major concern and server control is needed. | Ideal for large-scale, distributed systems or APIs that benefit from stateless and scalable authentication. |


### Actual Workflow

![Auth Schema](./schemas/authentication.svg)

Note: this workflow can be modified using .d2 file.

### How oAuth and social login work with Linked in?


#### Step 1: Redirect User to LinkedIn for Authorization
- **Action**: Generate a URL that redirects the user to LinkedIn's authorization page.
- **URL Parameters**:
  - `client_id`: Your application's client ID.
  - `redirect_uri`: The URL where LinkedIn should redirect the user after authorization.
  - `response_type=code`: Specifies that you want an authorization code.
  - `scope`: The permissions you are requesting (e.g., `r_emailaddress`, `r_liteprofile`).
- **User Experience**: The user is redirected to LinkedIn, where they log in and grant your app permission to access specific data.

> **Explanation**: This step initiates the OAuth2 flow. The `redirect_uri` is crucial because it ensures the user is redirected back to your app securely.

---

#### Step 2: User Authorizes Your App
- **Outcome**: After the user grants permission, LinkedIn redirects them to your specified `redirect_uri` with an **authorization code** in the query parameters.
- **Data You Receive**: The `authorization code` (a short-lived, single-use credential).
- **If Authorization Fails**: LinkedIn may redirect with an error instead.

> **Explanation**: The authorization code is not sensitive data. It is useless without your server's client secret and will be used in the next step to obtain an access token.

---

#### Step 3: Exchange Authorization Code for Access Token
- **Action**: Your backend server sends a POST request to LinkedIn’s token endpoint to exchange the authorization code for an **access token**.
- **Request Parameters**:
  - `grant_type=authorization_code`
  - `code`: The authorization code you received in Step 2.
  - `redirect_uri`: Must be the same `redirect_uri` used in Step 1.
  - `client_id`: Your application’s client ID.
  - `client_secret`: Your application’s client secret.
- **Response**: LinkedIn responds with an **access token** and possibly a **refresh token** (if applicable).
- **Data You Receive**: The `access token`, which is used to access the user's data securely.

> **Explanation**: This step ensures that the access token is exchanged securely between your backend and LinkedIn. The `client_secret` adds a layer of security, preventing unauthorized access.

---

#### Step 4: Fetch User Profile from LinkedIn
- **Action**: Use the access token to make an authenticated request to LinkedIn’s API (e.g., `https://api.linkedin.com/v2/me`) to fetch the user's profile.
- **Data You Retrieve**: Information such as:
  - `linkedin_id`: The unique identifier for the user on LinkedIn.
  - `first_name` and `last_name`
  - `email` (if requested and permissions are granted)
- **Use Cases**: Now, you have enough information to identify or create a user in your system.

> **Explanation**: The access token grants permission to access the user's profile data securely. This data is used to either log the user in or register them in your app.

---

#### Step 5: Check User Existence and Handle Different Scenarios
**Case 1: User Exists with LinkedIn ID**
- **Check**: Look up the user in your database using the `linkedin_id`.
- **Action**: If the user is found, log them in and create a session or generate an access token for your app.
- **Outcome**: The user is successfully logged in.

> **Explanation**: If a user with the `linkedin_id` already exists, it means they have previously logged in with LinkedIn, and you can authenticate them directly.

**Case 2: User Exists with the Same Email but No LinkedIn ID**
- **Check**: If no user is found with the `linkedin_id`, look for a user by their email.
- **Scenario**: The user signed up manually or with a different social login and hasn’t linked their LinkedIn account yet.
- **Options**:
  - **Option 1: Link Accounts**:
    - **Action**: Prompt the user to link their LinkedIn account to their existing profile.
    - **Verification**: You may require email verification or a confirmation step.
    - **Update**: If the user confirms, update their profile to include the `linkedin_id`.
  - **Option 2: Deny Automatic Linking**:
    - **Action**: Return an error and inform the user that an account with this email already exists. Prompt them to log in manually and link their LinkedIn account from their profile settings.
- **Outcome**: The user either links their accounts or is prompted to use their existing login method.

> **Explanation**: This case handles situations where an email conflict occurs. Linking accounts securely ensures that the user owns both accounts.

**Case 3: User Does Not Exist**
- **Check**: If no user is found by either `linkedin_id` or email, it is a new user.
- **Action**: Create a new user in your database with the following information:
  - `linkedin_id`
  - `email`
  - `first_name` and `last_name`
- **Outcome**: Log the user in, create a session, or generate an access token for your app.

> **Explanation**: This is the standard flow for registering a new user who logs in with LinkedIn for the first time.



### Additional Explanations
- **Why Use the Authorization Code Flow?**: The two-step process (getting a code first, then exchanging it for an access token) adds an extra layer of security by ensuring the access token is never exposed to the user's browser, reducing the risk of interception.
- **Access Token Storage**: If your app needs to make future requests to LinkedIn, you should store the access token securely, along with its expiration time, in your database.
- The `redirect_uri` used in Step 1 must be the same as the one used in Step 3 when exchanging the code for an access token. If they don’t match, the request will be rejected. The `redirect_uri` acts as a security measure to prevent unauthorized redirection and ensure the flow is consistent.
