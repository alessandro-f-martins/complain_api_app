#!/bin/bash

curl -d "@entry1.txt" -X POST http://localhost/complain
curl -d "@entry2.txt" -X POST http://localhost/complain
curl -d "@entry3.txt" -X POST http://localhost/complain
curl -d "@entry4.txt" -X POST http://localhost/complain
curl -d "@entry5.txt" -X POST http://localhost/complain
curl -d "@entry6.txt" -X POST http://localhost/complain
curl -d "@entry7.txt" -X POST http://localhost/complain
curl -d "@entry8.txt" -X POST http://localhost/complain

curl -d 'complain={"company":"Sala%20da%20Justiça"}' -X PATCH http://localhost/complain/5
