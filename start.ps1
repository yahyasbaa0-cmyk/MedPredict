# start.ps1
Write-Host "Started building containers... This may take a few minutes."
docker compose up --build -d

Write-Host "Containers are up! Waiting 5 seconds for services to initialize..."
Start-Sleep -Seconds 5

Write-Host "Applying database migrations..."
docker compose exec backend python manage.py makemigrations accounts patients appointments consultations prescriptions
docker compose exec backend python manage.py migrate

Write-Host "Creating admin user (admin / admin@example.com / admin)..."
# Create admin safely ignoring if it already exists
docker compose exec backend python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')"

Write-Host "AI training is deprecated. Using Groq API."

Write-Host "Project is running successfully!"
Write-Host "--------------------------------------------------------"
Write-Host "Frontend:    http://localhost:5173"
Write-Host "Backend API: http://localhost:8000/swagger/"
Write-Host "--------------------------------------------------------"
Write-Host "You can log in to the frontend with the username 'admin' and password 'admin'."
