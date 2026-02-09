from app.app import create_app, logger
from app.config import Config

if __name__ == '__main__':
    try:
        app = create_app()
        app.run(
            host='0.0.0.0',
            port=Config.PORT,
            debug=Config.FLASK_ENV == 'development'
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        exit(1)

