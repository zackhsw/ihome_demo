from . import api


@api.route('/v1.0/index')
def index():
    return "index page"
