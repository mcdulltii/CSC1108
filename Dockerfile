FROM pypy:3

WORKDIR /route_planner

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY .env ./
COPY . .

CMD [ "pypy3", "./app.py", "-f", "./web_scraper/routes.bin", "-i", "0.0.0.0", "-p", "80" ]
