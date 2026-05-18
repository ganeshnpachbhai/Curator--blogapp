from django.shortcuts import render,redirect
from .models import Employee
# Create your views here.
def home(request):
    context = {
        'employees':Employee.objects.all()
    }
    return render(request,'home.html',context) 
def add(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        position = request.POST['position']
        department = request.POST['department']
        salary = request.POST['salary']
        date = request.POST['date']
        employee = Employee(name=name,email=email,position=position,department=department,salary=salary,date=date)
        employee.save()
        return redirect('home')
    return render(request,'add.html')
def update(request,id):
    employee = Employee.objects.get(id=id)
    if request.method == 'POST':
        employee.name = request.POST['name']
        employee.email = request.POST['email']
        employee.position = request.POST['position']
        employee.department = request.POST['department']
        employee.salary = request.POST['salary']
        employee.date = request.POST['date']
        employee.save()
        return redirect('/')
    context={
        'employee':employee
    }
    return render(request,'update.html',context)
def delete(request,id):
    employee = Employee.objects.get(id=id)
    if request.method == 'POST':
        employee.delete()
        return redirect('/')
    context={
        'employee':employee
    }
    return render(request,'delete.html',context)
def details(request,id):
    employee = Employee.objects.get(id=id)
    context={
        'employee':employee
    }
    return render(request,'details.html',context)
