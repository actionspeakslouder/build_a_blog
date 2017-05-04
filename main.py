#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)


    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class MainPage(Handler):
    def render_front(self, title="", blog="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog "
                           "ORDER BY created DESC "
                            "LIMIT 5")
        self.render("base.html", title=title, blog = blog, error = error, blogs = blogs)

    def get(self):
        self.render_front()


class Blog(db.Model):
    title = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class NewPost(MainPage):

    def get(self):
        self.render("blog_entry.html")

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")

        if title and blog:
            b = Blog(title = title, blog = blog)
            b.put()
            self.redirect("/blog")
            self.write("thanks")
        else:
            error = "You need title and blog post"
            #self.write("this shit aint working")
            self.render("blog_entry.html",title = title, blog = blog , error= error)


class ViewPostHandler(MainPage):
    def get(self, id):
        post = Blog.get_by_id(int(id))

        self.write(post.title + "<br>" + "<br>" + post.blog)


app = webapp2.WSGIApplication([('/blog', MainPage),
                               ('/blog/newpost', NewPost),
                  webapp2.Route('/blog/<id:\d+>', ViewPostHandler)],
                              debug=True)
