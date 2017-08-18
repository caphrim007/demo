#!/bin/sh
python /root/demo/disc/discover_import.py --config /root/demo/disc/disc.config
sleep 5
python /root/demo/app/create_application.py --config /root/demo/app/app.config
sleep 5
python /root/demo/deploy/deploy_ltm.py --config /root/demo/deploy/deploy.config

