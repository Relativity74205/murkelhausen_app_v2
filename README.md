# murkelhausen_app_v2

## icons

https://lucide.dev/icons/trophy?search=waste

## docker

build

```bash
docker build -t reflex-simple-two-port .
```

run

```bash
docker run -p 3000:3000 -p 8000:8000 reflex-simple-two-port
```

publish

```bash
echo $GITHUB_PAT | docker login ghcr.io -u arkadius@schuchhardt.com --password-stdin
docker image tag murkel_app2:0.1.0 ghcr.io/relativity74205/murkel_app2:0.1.0
docker push ghcr.io/relativity74205/murkel_app2:0.1.0
```

# TODO

- [ ] Dockerfile
  - [ ] get requirements.txt from poetry
  - [x] write docker build script (local version dump and deploy, only major versions, local push)
- [ ] create overview page
- [ ] migrate old pages
  - [x] gym broich
    - create substate component for vertretungsplan
  - [x] fussball
  - [ ] weather
  - [x] mheg
- [ ] make api requests async and run in state background tasks
- [ ] write backend tests
- [ ] refactor:
  - [ ] move constants in backend to config file
  - [ ] change dto classes to rx.Base; replace tuple with list
- [ ] openAI Integration
  - [ ] voice! 
