@echo off
echo Starting Invoice Automation System...
cd C:\Users\luztow\Desktop\Invoice_Automation_sysytem
call invoice_env\Scripts\activate
cd invoice_project
waitress-serve --listen=127.0.0.1:8000 invoice_project.wsgi:application
pause

