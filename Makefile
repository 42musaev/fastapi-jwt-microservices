# Makefile for creating a service similar to

SERVICE_NAME := $(service)

create-service:
	mkdir -p $(SERVICE_NAME)/api $(SERVICE_NAME)/core $(SERVICE_NAME)/crud $(SERVICE_NAME)/db $(SERVICE_NAME)/models $(SERVICE_NAME)/schemas $(SERVICE_NAME)/services
	touch $(SERVICE_NAME)/ $(SERVICE_NAME)/Dockerfile
	touch $(SERVICE_NAME)/ $(SERVICE_NAME)/main.py
	touch $(SERVICE_NAME)/api/__init__.py
	touch $(SERVICE_NAME)/core/__init__.py
	touch $(SERVICE_NAME)/crud/__init__.py
	touch $(SERVICE_NAME)/db/__init__.py
	touch $(SERVICE_NAME)/models/__init__.py
	touch $(SERVICE_NAME)/schemas/__init__.py
	touch $(SERVICE_NAME)/services/__init__.py

.PHONY: create-service
