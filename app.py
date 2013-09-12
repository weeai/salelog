#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# Using tornado to build our logs system.
# Copyright(c) sales all rights reserved.

import os
import torndb
import tornado.web
import tornado.httpserver
import tornado.ioloop
import model
from tornado.options import define, options
define("port", default=3000, help="running on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', LoginHandler),
            (r'/login', LoginHandler),
            (r'/logout', AuthLogoutHandler),
            (r'/home', HomeHandler),
            (r'/log', LoggerHandler),
            (r'/log/detail', LogDetailHandler),
            (r'/logs', LoggerQueryHandler),
            (r'/user', UserHandler),
            (r'/user/(\d+)', UserDetailHandler),
            (r'/user/(\w+)', UserHandler),
            (r'/users', UserListHandler),
            (r'/myself', MySelfHandler),
            (r'/myself/password', MySelfHandler),
        ]
        settings = dict(
            cookie_secret="61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/",
            template_path=os.path.join(os.path.dirname(__file__), 'templates').replace("\\", "/"),
            static_path=os.path.join(os.path.dirname(__file__), 'static').replace("\\", "/"),
            debug=True
        )
        tornado.web.Application.__init__(self, handlers=handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        user = model.find_user_by_name_and_pwd(username, password)

        if user:
            user_cookie = tornado.escape.json_encode(user)
            self.set_secure_cookie("user", user_cookie)
            self.write("success")
        else:
            self.write("fail")


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect("/login")


class HomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = tornado.escape.json_decode(self.get_secure_cookie("user"))
        name = tornado.escape.xhtml_escape(user['username'])
        status = tornado.escape.xhtml_escape(user['status'])
        self.render("index.html", name=name, status=status)


class UserHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("user.html")

    def post(self, action):
        username = self.get_argument("username")
        password = self.get_argument("password")
        status = self.get_argument("status")
        if action == 'save':
            model.find_user_by_name(username)
            if user:
                self.write("exist")
                return
            model.save_user(username, password, status)
            self.write("success")
        elif action == 'update':
            user_id = int(self.get_argument("id"))
            models.update(username, password, status, user_id)
            self.write("success")


class UserDetailHandler(BaseHandler):
    def get(self, user_id):
        user = models.find_user_by_id(user_id)
        self.set_header("Content-Type", "application/json;charset=utf-8")
        self.write(tornado.escape.json_encode(user))
        self.finish()

    def post(self, user_id):
        model.delete_user_by_id(user_id)
        self.write("success")


class UserListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        page = int(self.get_argument("page"))
        rows = int(self.get_argument("rows"))
        count = model.user_count()
        users = model.find_user_by_pagination(page, rows)
        self.set_header("Content-Type", "application/json;charset=utf-8")
        self.write(tornado.escape.json_encode({'total': count["count"], "rows": users}))
        self.finish()


class MySelfHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = tornado.escape.json_decode(self.get_secure_cookie("user"))
        self.render("myself.html", user=user)

    def post(self):
        user_id = self.get_argument("id")
        pwd = self.get_argument("newPwd")
        confirm = self.get_argument("confirmPwd")
        if pwd is None or confirm is None:
            self.write("null")
        elif pwd != confirm:
            self.write("notequal")
        model.update_user_password(pwd, int(user_id))
        self.write("success")


class LoggerHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("log.html")


class LoggerQueryHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        page = int(self.get_argument("page"))
        rows = int(self.get_argument("rows"))
        logtime=self.get_argument('logtime', None)
        message = self.get_argument('message', None)
        
        count = model.log_count()
        rows = model.find_log_by_pagination(page, rows, logtime, message)
        for log in rows:
            log['logtime'] = log['logtime'].strftime("%Y-%m-%d %H:%M:%S")
        self.set_header('Content-Type', "application/json;charset=utf-8")
        self.write(tornado.escape.json_encode({"total": count['count'], "rows": rows}))
        self.finish()

class LogDetailHandler(BaseHandler):
    def get(self):
        log_id = int(self.get_argument('id'))
        logtime = self.get_argument("logtime")
        row = model.find_log_by_id_and_logtime(log_id, logtime)
        self.render('log_detail.html', log=row)


if __name__ == '__main__':
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()



