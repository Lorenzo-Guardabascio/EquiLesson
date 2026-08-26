from django.urls import path

from . import views

app_name = "report"

urlpatterns = [
    path("", views.report, name="report"),
    path("export/csv/", views.report_csv, name="report_csv"),
    path("export/pdf/", views.report_pdf, name="report_pdf"),
]
