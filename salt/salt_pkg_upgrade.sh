#!/bin/bash

sudo salt \* pkg.refresh_db
sudo salt \* pkg.upgrade
