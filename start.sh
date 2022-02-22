#!/bin/bash
app="webhoockdecript"
docker build -t ${app} .
docker run -d -p 56733:80 \
  --name=${app} \
  -e "LETSENCRYPT_HOST=hk.ed0cyawkrad.duckdns.org,www.hk.ed0cyawkrad.duckdns.org" \
  -e "LETSENCRYPT_mail=alu0101105802@ull.edu.es" \
  -e "VIRTUAL_HOST=hk.ed0cyawkrad.duckdns.org,www.hk.ed0cyawkrad.duckdns.org" \
  -e "PARSE_SERVER_MASTER_KEY=34xxABCDxx56" \
  -e "PARSE_SERVER_APLICATION_ID=e0ef0e30-b8e6-11eb-8529-0242ac130003" \
  -e "PARSE_SERVER_URL=app.ed0cyawkrad.duckdns.org" \
  --network=parse_default \
  -v $PWD:/app ${app} 
