# Architecture

## Back-end Architecture

I thought to at least 3 different ones for a fastAPI project:

| Name                          | Description                                                                 | Name of Directories                      | Pros                                                                                                   | Cons                                                                                                        |
|-------------------------------|-----------------------------------------------------------------------------|------------------------------------------|--------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| **Fat Model Architecture**     | Architecture where business logic is embedded within the models (like Django's "Fat Models" pattern).               | `routes/`, `models/`                     | Easy to follow for smaller projects; logic stays close to the data; widely used in frameworks like Django. | Leads to "fat models" that are harder to maintain and scale; tightly coupled responsibilities complicate refactoring. |
| **Basic Layered Architecture** | A simple architecture where the business logic is mixed directly with routes or handled in a separate logic layer. | `routes/`, `models/`, `logic/`           | Simple and easy to understand; minimal layers; suitable for small projects.                              | Harder to scale for larger apps; mixing of concerns between data and logic; testing and maintenance become complex. |
| **Repository Pattern**         | A layered architecture with clear separation: services handle business logic, repositories handle CRUD.            | `routes/`, `models/`, `services/`, `repositories/` | Strong separation of concerns; scalable; repositories abstract database logic; easier to test and maintain. | More complex and introduces boilerplate; can add unnecessary layers for smaller projects.                   |


While the fat model architecture is not widely used in FastAPI projects, I decided to go with it for now, keeping in mind it should be updated if the project grows over time. Mixins are used to make models thiner.
