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
- [ ] show version
- [ ] create overview page
  - [ ] weather
  - [ ] todays appointments
  - [ ] children hat sport or swimming
  - [ ] ...
- [ ] migrate old pages
  - [x] gym broich
    - create substate component for vertretungsplan
  - [x] fussball
  - [ ] weather
  - [ ] ruhrbahn
  - [x] mheg
  - [ ] power
  - [ ] garmin
- [ ] create new pages
  - [ ] nine
  - [ ] calendar
  - [ ] openAI
- [ ] make api requests async and run in state background tasks
- [ ] write backend tests
- [ ] refactor:
  - [ ] move constants in backend to config file
  - [ ] change dto classes to rx.Base; replace tuple with list
- [ ] openAI Integration
  - [ ] voice!

## Google Authentification

- [google project](https://console.cloud.google.com/apis/dashboard?project=murkelhausen)
- [service account](https://console.cloud.google.com/iam-admin/serviceaccounts/details/100602016701161296682;edit=true?previousPage=%2Fapis%2Fcredentials%3Fproject%3Dmurkelhausen&project=murkelhausen)
  - service account id/email: murkelhausen2@murkelhausen.iam.gserviceaccount.com
- [medium article](https://medium.com/iceapple-tech-talks/integration-with-google-calendar-api-using-service-account-1471e6e102c8)