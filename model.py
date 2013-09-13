#!usr/bin/env python
#-*- coding:utf-8 -*-
#Using tornado to build our log system
#Copyright(c) sales all rights reserved.
import torndb

from tornado.options import define, options
define("mysql_host", default="localhost:3306", help="mysql db host")
define("mysql_database", default="logs", help="mysql db name")
define("mysql_user", default="root", help="mysql username")
define("mysql_password", default="root", help="mysql password")


#get mysql connection
db = torndb.Connection(
    host=options.mysql_host,
    database=options.mysql_database,
    user=options.mysql_user,
    password=options.mysql_password
)


#find user by username and password
def find_user_by_name_and_pwd(username, password):
    return db.get("SELECT id, username, status FROM users WHERE username=%s and password=%s ", username, password)


#find user by username
def find_user_by_name(username):
    return db.get("SELECT username FROM users WHERE username = %s", username)

#save user
def save_user(username, password, status):
    sql = "INSERT INTO users(username, password, status) VALUES(%s, %s, %s)"
    db.execute(sql, username, password, status)

def update_user(username, password, stauts, user_id):
    sql = "UPDATE users SET username='%s', password='%s', status='%s' where id=%d" % (username, password, status, user_id)
    db.execute(sql)

#find user by id
def find_user_by_id(id):
    sql = "SELECT id, username, status FROM users WHERE id=%d" % int(user_id)
    return db.get(sql)


#delete user by id
def delete_user_by_id(user_id):
    sql = "DELETE FROM users where id = %d" % int(user_id)
    db.execute(sql)


#user count
def user_count():
    return db.get("SELECT count(id) as count FROM users")


#user pagination
def find_user_by_pagination(page, rows):
    start = (page -1) * rows
    offset = start + rows
    sql = "SELECT id, username, status FROM users ORDER BY id desc LIMIT %d, %d" % (start, offset)
    return db.query(sql)


#update user password
def update_user_password(pwd, user_id):
    sql = "UPDATE users set password='%s' WHERE id=%d" % (pwd, user_id)
    db.execute(sql)


#log count
def log_count(logtime=None, message=None):
    sql = "SELECT count(*) as count FROM sales30_system_log WHERE 1=1"
    if logtime:
        sql += " AND logtime>='%s'" % logtime
    if message:
        sql += " AND message like '%%"+message+"%%'"
    return db.get(sql)


#find log by pagination
def find_log_by_pagination(page, rows, logtime=None, message=None):
    start = (page-1) * rows
    offset = start + rows
    sql = "SELECT id, logtime, message FROM sales30_system_log WHERE 1=1 "
    if logtime:
        sql += " AND logtime>='%s' " % logtime
    if message:
        sql += " AND message like '%%"+message+"%%'"

    sql +=" ORDER BY logtime desc LIMIT %d, %d" % (start, offset)
    print sql
    return db.query(sql)

#find log by id and logtime
def find_log_by_id_and_logtime(log_id, logtime):
    sql = "SELECT * FROM sales30_system_log WHERE id = %d and logtime='%s'" % (log_id, logtime)
    return db.get(sql)
