project ?= auto
version ?= auto

develop:
	pip install -t lib -r requirements.txt

create-client-secrets:
	gcloud iam service-accounts create \
		groupkit-app-engine-bot \
		--project=$(project) \
		--display-name "GroupKit App Engine Bot"
	gcloud iam service-accounts keys create \
		client_secrets.json \
		--project=$(project) \
		--iam-account groupkit-app-engine-bot@$(project).iam.gserviceaccount.com

deploy:
	gcloud app deploy \
	  -q \
	  --project=$(project) \
	  --version=$(version) \
	  --verbosity=error \
	  --no-promote \
	  app.yaml

run:
	dev_appserver.py --port=8080 .
