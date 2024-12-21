### Critics of SQLModel

SQLModel seems to be the way to go in FastAPI tutorial. Is it justified, or is the author (same than FastAPI) too pushy about its own tool?
Here are some negative aspects that.


- More example of SQLAlchemy outside (especially with external packages I'd like to copy)
- Additional layer of abstraction => hard to understand what's happening behind the scene, hard know when to imports things from SQLModel or SQLAlchemy. SQLAlchemy is already an abstraction layer.
- The main promise to avoid duplication does not work
  - e.g. data validation does not work when `table=True` is set, and even worst, this happens **silently**. 
- Uncertain support over time: author does not answer on some issues with lots of users claming the same things
- External tools like [Polyfactory](https://polyfactory.litestar.dev/latest/) would be easier to integrate
- Pydantic Models would be easier to share if not mixed with SQLModel ones.
- Writing custom fields like PositionField would be easier when there is a single tool to use (plus, code from the internet car be used)
- Using SQLModel creates lock-in to the framework. Having pure SQLAlchemy would allow to migrate to Litestar or Flask

#### Other Quotes

> sqlalchemy now provides a data class meta object. It allows you to mark your models as data classes. This means you can now use them in fastapi!

> I find it lacking every time it wasn’t just a dumb CRUD wrapper.

> I have no idea why someone would want to mix the models from validation of input and output and db models. They are not the same thing.

> If you have a lot of business logic, then you are mixing several distinct models: domain or entity models, tables models, and dtos. I think is not well suited for a large enterprise application.

> SQLAlchemy is there to be a 1-1 connection to my database tables or views, pydantic is there to validate data on arrival, these are two different things I like to keep separated

> A big benefit for us [to use SQLAlchemy] was that we were able to pull out the Pydantic Models into a separate package and reuse that across the server and multiple client applications.

> I’m not a fan of adding another abstraction over SQLAlchemy. SQLAlchemy itself is already an abstraction, but it doesn’t hide the low-level details, allowing you to handle complex queries effectively.

> [With SQLModel] You then realize that the table class and the non-table ones cover in fact two separate aspects, and you just saved a few lines of repeated class arguments. With all sorts of drawbacks that comes with this high abstractions.

> I always felt awkward with ORM classes being so tightly coupled to DB tables which makes the domain classes hard to use in isolation. e.g., ORM assumes that you need a session when perhaps you have some behavior that doesn't involve the DB.

> I don’t see any point to use sqlmodel cause in the end I had to import some sqlalchemy internals to make it work.

> In my experience SQLModel obscures a lot of functionality which is provided by SQLalchemy

> SQLModel was launched **before** the release of `Mapped[]` feature. So it may be less relevant.

Resources
- https://www.reddit.com/r/FastAPI/comments/1h6mxwg/comment/m0id8hr/?context=3
- https://www.youtube.com/watch?v=GONyd0CUrPc&themeRefresh=1
- https://github.com/fastapi/sqlmodel/issues/52#issuecomment-1866786116
