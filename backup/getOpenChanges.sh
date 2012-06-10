#!/bin/bash
psql -U gerrit2_ro -c "select ac.ssh_user_name,changes.change_id,changes.open from changes,accounts as ac WHERE changes.owner_account_id=ac.account_id" reviewdb

