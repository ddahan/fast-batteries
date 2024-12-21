# Settings / parameters

### Theory

There exists 3 different kinds of global settings used in this project:

| Setting Type         | Usage                                                                 | Change Method                                                        | Change Application      | Example                             |
|----------------------|----------------------------------------------------------------------|----------------------------------------------------------------------|-------------------------|-------------------------------------|
| **Hardcoded settings**    | Stable settings that change infrequently.                            | Commit the new config file.                                           | On new deployment.       | `APP_NAME` ("The Cook Book")        |
| **Environment settings**  | Stable settings but which differ according to the environment.            | Update `.env` file (local) or server env vars (remote).               | On server restart.       | `DEBUG` (`True` in local, `False` in production) |
| **Database parameters**   | Typically used for more dynamic, business-driven settings.           | Any tool that can change a database row (admin tool, dedicated website). | No specific action required. | `APP_TAGLINE` ("The best cooking app on the market") |


> Sidenote: there exists other database settings related to users

### Pydantic settings

Pydantic Settings is very helpful to manage both hardcoded settings and environment settings. Basically:
- a `BaseSettings` attribute with a default value will be an hardcoded setting.
- a `BaseSettings` attribute without a default value will be read from the `.env`file.
