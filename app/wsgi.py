
from .app import application
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = DispatcherMiddleware(app=None, mounts={
    '/': application, # Set the subpath for the app in the domain
})

if __name__ == "__main__":

    # app.run(port=5001) # Execute in the subpath
    
    application.run(port=5001) # Exceute in the domain
