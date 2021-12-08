FROM mysql:latest

ENV MYSQL_DATABASE=alinedb
ENV MYSQL_ROOT_PASSWORD=Kw990318!
   
COPY aline.sql /docker-entrypoint-initdb.d
