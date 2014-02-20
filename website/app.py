# coding: utf-8
import web
import os

t_globals = {
    'datestr': web.datestr
}

render = web.template.render('{0}/templates'.format(os.path.dirname(os.path.abspath(__file__))), globals=t_globals, cache=False)

urls = (
    '/', 'index',
)
 
class index:
    def GET(self):
        return render.index()

wsgiapp = web.application(urls, globals()).wsgifunc()

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.internalerror = web.debugerror
    app.run()
