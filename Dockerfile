FROM python:3-alpine AS builder

WORKDIR /app

RUN python3 -m venv venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

# Stage 2
FROM python:3-alpine AS runner

ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PORT=8000

WORKDIR /app

COPY --from=builder /app/venv venv
COPY src src

# Aggiungi regole del firewall
RUN iptables -A INPUT -s 0.0.0.0/0 -j ACCEPT

EXPOSE ${PORT}

#CMD gunicorn --bind :${PORT} --workers 2 example_django.wsgi
CMD python3 public/app.py
