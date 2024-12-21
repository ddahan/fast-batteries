## How to deploy in production


### About local/prod parity

There are some differences between local and remote containers:

- local compose uses a related `devcontainer.json` for better VS Code integration
- VS Code dev containers do not support a single workspace for multiple containers. As a workaround, nuxt and fastAPI services are installed on the same container on local.
- local containers use raw images while prod containers use `Dockerfile` files (to fine-tune the remote build)
- A temporary container exists on prod container to run migrations, not in local.
- Volumes have the same names, but this has no importance.
- In remote environment, traekik is able to point directly to containers, so there's no need to forward ports to host. On the contrary, on local, it's necessary. Note that ports are managed entirely in `docker-compose.yaml` (not in `devcontainer.json`) to avoid additional complexity.

Note that Docker Compose inheritance is not used, as it adds unjustified complexity in my opinion.
