# facecmp
A dockerized python service to which a image can be posted to that then tries to match it with something in it's database

```bash
docker build -t w2wizard/facecmp .
docker run -p 4242:4242 -v ./db/:/app/db/ w2wizard/facecmp
```