# Local Install

#### Install locally

**Method 1** (recommended): use VS Code devcontainer:
  - Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - Install [VS Code Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
  - Run "Clone Repository in Container Volume" and follow instructions.
  - Create .env files in `back/` and `front/` repository, following `.env.example` files.

**Method 2**: install it like any [Poetry](https://python-poetry.org/) project, and with you desired database.

#### Run locally

- front-end: `cd front; npm run dev`
- back-end: `cd back; fastapi dev`

#### Useful tasks

- TS interface generation: `cd front; npm run schemas`


#### Run Celery/beat worker

- Use VS Code command `Run task` and then chose `Celery`.
