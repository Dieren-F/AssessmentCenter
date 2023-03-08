FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /AssessmentProject
COPY Pipfile Pipfile.lock /AssessmentProject/
RUN pip install pipenv && pipenv install --system
COPY . /AssessmentProject/