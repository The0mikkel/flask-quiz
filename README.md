# Flask quiz application

![GitHub license](https://img.shields.io/github/license/the0mikkel/flask-quiz) ![GitHub issues](https://img.shields.io/github/issues/the0mikkel/flask-quiz) ![GitHub pull requests](https://img.shields.io/github/issues-pr/the0mikkel/flask-quiz) ![GitHub last commit](https://img.shields.io/github/last-commit/the0mikkel/flask-quiz)

Simple Flask quiz application, made using flask 3 and wsgi.

## Running the application

The application is made to run in Docker. An included docker-compose file will build the image and run the container. To run the application, run the following command in the root directory of the project:

```bash
docker compose build
docker compose up
```

Please note, that a `.env` file is required to run the application. The `.env` file should contain the following variables:

```.env
SECRET_KEY
```

An example `.env` file is included in the repository as `.env.example`.

*Please note, there have been prepared for nginx reverse proxy, and therefore requires the external network to be named "nginx-proxy". The CLI will prompt you to create the network if it does not exist.*  
*It can be deleted from the docker-compose file if not needed.*

## License

Please see LICENSE file for license details.

## Contribution

To contribute, please fork the repository and create a pull request.  
If you find bugs or have suggestions for improvements, please create an issue.

## Authors and acknowledgment

This project was made by [Mikkel Albrechtsen](https://github.com/the0mikkel) using GitHub Copilot.
