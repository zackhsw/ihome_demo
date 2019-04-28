from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from ihome import create_app, db

# flask应用对象
app = create_app("develop")
manager = Manager(app)
Migrate(app, db)
manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    app.run()
