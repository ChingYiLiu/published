FROM python:3.11.3
#FROM tiangolo/uvicorn-gunicorn:python3.11-slim

ENV TZ="Asia/Taipei"
RUN date

RUN apt-get update && apt-get install -y htop nload telnet vim procps netcat wget curl net-tools dnsutils
RUN mkdir -p /root
RUN echo "# alias    \n\
PS1='\[\033[01;36m\]\w\[\033[00m\]\\n\[\033[01;32m\]\u@\h\[\033[00m\] # '  \n\
alias ls='ls --color=auto' \n\
alias ll='ls -altr'  \n\
alias l='ls -al'   \n\
alias h='history'  \n\
set -o vi          \n"\
> /root/.bashrc

COPY requirements.txt /usr/src/requirements.txt

RUN set -eux; \
   \
   pip install --upgrade pip;

RUN set -eux; \
   \
   pip install --no-cache-dir -r /usr/src/requirements.txt;


EXPOSE 8080

COPY ./service /service
RUN ls -l service/config/config.yml

# Use the ping endpoint as a healthcheck,
# so Docker knows if the API is still running ok or needs to be restarted
HEALTHCHECK --interval=61s --timeout=3s --start-period=60s CMD curl --fail http://localhost:8080/ping || exit 1

CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8080", "--log-config", "service/config/log_conf.yml"]
# uvicorn service.main:app --host 0.0.0.0 --port 8080 --log-config service/config/log_conf.yml
