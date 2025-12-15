Docker Compose
```
services:
  proxyki-invites-bot:
    container_name: proxyki-invites-bot
    build: https://github.com/Tim-oxa/proxyki-invites.git
    restart: always
    env_file: .env
```
