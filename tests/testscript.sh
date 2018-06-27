#!/bin/bash

curl -d "@linha1.txt" -X POST http://localhost/complain
curl -d "@linha2.txt" -X POST http://localhost/complain
curl -d "@linha3.txt" -X POST http://localhost/complain
curl -d "@linha4.txt" -X POST http://localhost/complain
curl -d "@linha5.txt" -X POST http://localhost/complain
curl -d "@linha6.txt" -X POST http://localhost/complain
curl -d "@linha7.txt" -X POST http://localhost/complain
curl -d "@linha8.txt" -X POST http://localhost/complain

curl -d 'complain={"company":"Sala%20da%20Justiça"}' -X PATCH http://localhost/complain/5
