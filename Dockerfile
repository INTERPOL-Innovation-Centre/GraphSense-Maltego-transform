FROM python:3.8-slim-buster
LABEL Name=maltego-trx Version=0.0.1
EXPOSE 8080
RUN mkdir -p /var/www/TRX/
WORKDIR /var/www/TRX/
# Copy python requirements file
COPY requirements.txt requirements.txt
# Install maltego-trx and gunicorn
RUN pip3 install -r requirements.txt
# Copy project file and transforms
COPY project.py /var/www/TRX/
COPY extensions.py /var/www/TRX/
COPY settings.py /var/www/TRX/
COPY favicon.ico /var/www/
COPY graphsense /var/www/TRX/graphsense/
COPY transforms /var/www/TRX/transforms/
RUN chown -R www-data:www-data /var/www/TRX/
CMD ["python", "project.py", "runserver"]