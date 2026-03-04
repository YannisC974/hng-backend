# 🏆 Gamification & Wellness API - Core Backend

![CI Status](https://github.com/YannisC974/hng-backend/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=flat&logo=django)
![Docker](https://img.shields.io/badge/Docker-Production_Ready-2496ED?style=flat&logo=docker)

## 📖 Overview
Developed as the core backend infrastructure for a Berlin-based health-tech startup, this RESTful API powers a gamified wellness application designed to boost user engagement and retention. 

The platform motivates users (primarily university students) to build healthy daily routines through a polymorphic challenge system, live community events, and a comprehensive reward engine. The architecture has been hardened to meet modern production standards, emphasizing security, containerization, and automated CI/CD pipelines.

---

## ✨ Core Domain Features

The system is modularly designed around 4 key business domains:

### 👤 Identity & Access Management (`Accounts`)
* **Secure Authentication**: Implementation of robust JWT (JSON Web Token) authentication using `HttpOnly` cookies to prevent XSS attacks.
* **User Profiling & Tracking**: Custom user models tracking detailed demographics (university, geographic regions) and engagement metrics (consecutive active days).

### 🎯 Gamification Engine (`Challenges`)
* **Dynamic Daily Routines**: A daily unlock system delivering varied content: Intense/Moderate Physical workouts, Mental cognitive tasks, and Social interactions.
* **Instructor Integration**: Content linked to platform partners and instructors with integrated social media and video streaming capabilities.

### 🎁 Reward System (`Prizes`)
* **Dual-Layered Gratification**: 
  * **Short-term**: Daily sponsor giveaways with access codes and promotional media.
  * **Long-term**: A persistent achievement showcase where users unlock virtual *Medals*, *Badges*, and *Trophies* based on milestone completion.

### 📅 Community Events (`Events`)
* **Live Event Management**: Scheduling and RSVP system for virtual or physical community gatherings.
* **Time-gap Filtering**: Custom API views to fetch upcoming events dynamically within a specific rolling window.

---

## 🛠️ Tech Stack & DevOps Architecture

This project strictly adheres to DevOps best practices and "Twelve-Factor App" methodology.

* **Core Stack**: Python 3.11, Django 5.2, Django Rest Framework (DRF), PostgreSQL.
* **Server**: `Gunicorn` WSGI server, optimized by utilizing in-memory temp directories (`--worker-tmp-dir /dev/shm`) for maximum I/O performance.
* **Container Security (Hardening)**:
  * Principle of Least Privilege: Container runs as a dedicated, non-root `django` user.
  * Immutable Infrastructure: The source code volume is mounted as **Read-Only (`:ro`)** to prevent malicious runtime modifications.
* **CI/CD & Quality Assurance**: 
  * Automated testing via **Pytest**.
  * Strict formatting enforcement using `pre-commit` hooks (**Black**, **Isort**, **Flake8**).
  * CI pipeline powered by **GitHub Actions**.

---

## 🚀 Getting Started (Developer Experience)

The development environment is fully containerized. You only need Docker installed on your machine.

```bash
# 1. Clone the repository
git clone [https://github.com/YannisC974/hng-backend.git](https://github.com/YannisC974/hng-backend.git)
cd hng-backend

# 2. Setup environment variables
cp .env.exemple .env
# Fill in your local variables in the .env file

# 3. Spin up the infrastructure (Database + API)
docker compose up -d --build

# 4. Run database migrations
docker compose exec web python manage.py migrate

# 5. Create a superuser for admin access
docker compose exec web python manage.py createsuperuser