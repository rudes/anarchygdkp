FROM python:3.9-alpine3.15

WORKDIR /bot
ADD . /bot
RUN pip install --disable-pip-version-check -q -r requirements.txt

ENTRYPOINT [ "python", "bot.py" ]
